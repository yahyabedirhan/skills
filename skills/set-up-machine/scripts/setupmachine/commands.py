"""Shell command text -> the simple commands it runs, and whether a command row covers one.

The pre-tool hook reads a command the way the shell would run it, so a rule
catches every spelling of the same command:

- compound commands are split on `&&`, `||`, `;`, `|`, `&`, newlines and
  parentheses, and command substitutions (`$(…)`, backticks) are read too;
- leading `VAR=value` words, shell keywords (`then`, `do`, `{`, `!`) and
  wrappers (`timeout`, `nice`, `nohup`, `env`, `xargs`, `command`, …) are dropped;
  a wrapper that runs no command is read as itself alone (`env -u X` -> `env`);
- a program named by path (`/bin/rm`) is read by its basename, in lower case where
  the filesystem ignores case (macOS runs `/bin/rm` for `RM`; Linux finds no `RM`);
- the command inside `bash|sh|zsh -c '…'` (any flag cluster holding `c`, such as
  `-lc`), `eval`, `sudo`, `find -exec`, a heredoc or a pipe into a shell is read
  as a command of its own;
- flags are read anywhere after the program (`git push origin main --force`,
  `rm x -rf`), clustered or not (`-rfv`), until `--`.

Standard library only: it runs on macOS's Python 3.9.
"""
from __future__ import annotations

import os
import re
import shlex
import sys

# Whether program names are read case-insensitively: macOS's and Windows's default
# filesystems find `/bin/rm` for `RM`, Linux's don't.
FOLD_CASE = sys.platform in ("darwin", "win32")
SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
# Shell options that take the next word as their value.
SHELL_VALUE_OPTIONS = {"-o", "+o", "-O", "+O", "--rcfile", "--init-file"}
# Words that start a command without being its program.
KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "{", "}"}
# Wrappers run the command after their own options; the value each option takes is skipped.
WRAPPERS = {
    "builtin": set(),
    "caffeinate": {"-t", "-w"},
    "command": set(),
    "doas": {"-u", "-C"},
    "env": {"-u", "-C", "-P", "--unset", "--chdir"},
    "exec": {"-a"},
    "ionice": {"-c", "-n", "-p"},
    "nice": {"-n", "--adjustment"},
    "nohup": set(),
    "noglob": set(),
    "stdbuf": {"-i", "-o", "-e"},
    "sudo": {"-u", "-g", "-C", "-D", "-h", "-p", "-r", "-t", "-U", "-T", "-R"},
    "time": {"-o", "-f"},
    "timeout": {"-s", "-k", "--signal", "--kill-after"},
    "xargs": {"-I", "-J", "-L", "-n", "-P", "-d", "-s", "-E", "-a", "-R", "-S", "--delimiter", "--max-args",
              "--max-procs", "--arg-file", "--replace", "--max-lines", "--eof", "--max-chars"},
}
# Wrappers whose first word after the options is theirs, not the command's.
WRAPPER_POSITIONALS = {"timeout": 1}
# Options that make `command` look a name up instead of running it.
LOOKUP_ONLY = {"command": {"-v", "-V"}}
FIND_EXEC = {"-exec", "-execdir", "-ok", "-okdir"}

PUNCTUATION = "();<>|&\n`"
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\+?=")
HEREDOC = re.compile(r"(?<!<)<<(-?)\s*(['\"]?)([A-Za-z_][\w.-]*)\2")
FEEDS_A_SHELL = re.compile(r"(^|[\s|;&(`])(\S*/)?(bash|sh|zsh|dash|ksh|eval|source)(\s|$)")
MAX_DEPTH = 8


def simple_commands(text: str, depth: int = 0) -> list:
    """Every simple command the text runs, as argv lists with the program as a basename."""
    if depth > MAX_DEPTH or not text.strip():
        return []
    text = text.replace("\\\n", "")
    text, shell_bodies = _heredocs(text)
    out = []
    for body in shell_bodies:
        out += simple_commands(body, depth + 1)
    segments = []  # (words, the separator before them)
    words, before, redirect = [], "", None
    for token in _tokens(text) + [";"]:
        if _is_punctuation(token):
            if "<" in token or ">" in token:
                redirect = token
                continue
            if words:
                segments.append((words, before))
            words, before, redirect = [], token, None
            continue
        for inner in _substitutions(token):
            out += simple_commands(inner, depth + 1)
        if redirect is not None:
            if redirect == "<<<" and any(os.path.basename(w) in SHELLS for w in words):
                out += simple_commands(token, depth + 1)  # a here-string fed to a shell
            redirect = None
            continue
        words.append(token)
    for i, (words, before) in enumerate(segments):
        for argv in _unwrap(words, depth):
            out.append(argv)
            if before in ("|", "|&") and _reads_stdin_as_shell(argv) and i:
                for word in segments[i - 1][0][1:]:  # `echo "rm -rf x" | sh`
                    out += simple_commands(word, depth + 1)
    return out


def _tokens(text: str) -> list:
    lexer = shlex.shlex(text, posix=True, punctuation_chars=PUNCTUATION)
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError:  # an unclosed quote: read the words without quoting
        return re.findall(r"[^\s;&|()<>'\"]+|[;&|()\n]+|[<>]+", text)


def _is_punctuation(token: str) -> bool:
    return bool(token) and all(c in PUNCTUATION for c in token)


def _heredocs(text: str):
    """The text without heredoc bodies, and the bodies that feed a shell (`bash <<EOF`)."""
    lines, kept, bodies, i = text.split("\n"), [], [], 0
    while i < len(lines):
        line = lines[i]
        kept.append(line)
        i += 1
        for m in HEREDOC.finditer(line):
            body = []
            while i < len(lines):
                current = lines[i]
                i += 1
                if (current.lstrip("\t") if m.group(1) else current) == m.group(3):
                    break
                body.append(current)
            if FEEDS_A_SHELL.search(line):
                bodies.append("\n".join(body))
    return "\n".join(kept), bodies


def _substitutions(word: str) -> list:
    """Commands inside `$(…)` and backticks in a word the lexer kept whole (a quoted string)."""
    found = []
    start = word.find("$(")
    if start != -1:
        end = word.rfind(")")
        found.append(word[start + 2:end] if end > start else word[start + 2:])
    parts = word.split("`")
    found += [parts[k] for k in range(1, len(parts), 2)]
    return found


def _unwrap(words: list, depth: int) -> list:
    """The command itself, then every command it runs inside it."""
    argv = _strip(words)
    if not argv:
        return []
    out = [argv]
    program, args = argv[0], argv[1:]
    inner_text, inner_argv = None, None
    if program in SHELLS:
        inner_text = _shell_string(args)
    elif program == "eval":
        inner_text = " ".join(args)
    elif program == "find":
        start = next((k for k, a in enumerate(args) if a in FIND_EXEC), None)
        if start is not None:
            inner_argv = [a for a in args[start + 1:] if a not in ("{}", "+")]
    if program in ("sudo", "doas"):
        inner_argv = _after_options(args, WRAPPERS[program])
    if inner_text:
        out += simple_commands(inner_text, depth + 1)
    if inner_argv:
        out += _unwrap(inner_argv, depth + 1)
    return out


def _strip(words: list) -> list:
    """Drop assignments, keywords and wrappers; the program becomes its basename (see _program)."""
    i = 0
    while i < len(words):
        word = words[i]
        name = _program(word)
        if ASSIGNMENT.match(word) or word in KEYWORDS:
            i += 1
        elif name in WRAPPERS and name not in ("sudo", "doas"):
            rest = words[i + 1:]
            if name == "env":
                rest = _split_env_string(rest)
                words = words[:i + 1] + rest
            if any(a in LOOKUP_ONLY.get(name, ()) for a in rest[:1]):
                return []
            rest = _after_options(rest, WRAPPERS[name])
            rest = rest[WRAPPER_POSITIONALS.get(name, 0):]
            if not rest:
                return [name]  # a wrapper that runs nothing does its own job: `env -u X` prints the environment
            i = len(words) - len(rest)
        else:
            break
    argv = words[i:]
    if not argv:
        return []
    return [_program(argv[0]) or argv[0], *argv[1:]]


def _program(word: str) -> str:
    """A program's basename, in lower case where the filesystem ignores case (FOLD_CASE)."""
    name = os.path.basename(word.lstrip("\\"))
    return name.lower() if FOLD_CASE else name


def _split_env_string(args: list) -> list:
    """`env -S 'rm -rf x'` runs the words of its string: put them in place of the option."""
    for k, a in enumerate(args):
        if a in ("-S", "--split-string") and k + 1 < len(args):
            value, after = args[k + 1], args[k + 2:]
        elif a.startswith("--split-string="):
            value, after = a.split("=", 1)[1], args[k + 1:]
        elif a.startswith("-S") and len(a) > 2:
            value, after = a[2:], args[k + 1:]
        else:
            continue
        try:
            split = shlex.split(value)
        except ValueError:
            split = value.split()
        return args[:k] + split + after
    return args


def _after_options(args: list, value_options: set) -> list:
    """What follows a wrapper's own options (and, for env and sudo, its VAR=value words)."""
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--":
            return args[i + 1:]
        if a.startswith("-") and len(a) > 1:
            i += 2 if a in value_options else 1
        elif ASSIGNMENT.match(a):
            i += 1
        else:
            break
    return args[i:]


def _shell_string(args: list):
    """The command string of `sh -c '…'` (or `-lc`, `-ec`, …), or None."""
    has_c, i = False, 0
    while i < len(args):
        a = args[i]
        if a == "--":
            i += 1
            break
        if a in SHELL_VALUE_OPTIONS:
            i += 2
            continue
        if a[:1] in ("-", "+") and len(a) > 1:
            if not a.startswith("--") and "c" in a[1:]:
                has_c = True
            i += 1
            continue
        break
    return args[i] if has_c and i < len(args) else None


def _reads_stdin_as_shell(argv: list) -> bool:
    if argv[0] not in SHELLS:
        return False
    return not any(not a.startswith(("-", "+")) for a in argv[1:]) and _shell_string(argv[1:]) is None


# --- matching a command row ---------------------------------------------------


def program_matches(rule, program: str) -> bool:
    """`mkfs` covers `mkfs.ext4`: a program's dotted variants are the same program."""
    return any(program == p or program.startswith(p + ".") for p in rule.programs)


def covers(rule, argv: list) -> bool:
    """Whether a command row covers this normalised argv, whatever the flag order or position."""
    if not argv or not program_matches(rule, argv[0]):
        return False
    if rule.bare:
        return len(argv) == 1
    flags, words = _flags_and_words(argv)
    if not all(any(name in flags for name in group) for group in rule.flags):
        return False
    for sub in rule.subcommands:
        for start in range(len(words) - len(sub) + 1):
            if tuple(words[start:start + len(sub)]) != sub:
                continue
            after = words[start + len(sub):]
            if tuple(after[:len(rule.operands)]) == rule.operands:
                return True
    return False


def _flags_and_words(argv: list):
    """Flag names (short letters and long names) and the other words, read past operands until `--`.

    A shell's own options end at its first operand; after that the words are
    its script's arguments.
    """
    flags, words, ended = set(), [], False
    stops_at_operand = argv[0] in SHELLS
    skip = False
    for a in argv[1:]:
        if skip:
            skip = False
        elif stops_at_operand and not ended and a in SHELL_VALUE_OPTIONS:
            skip = True
        elif not ended and a == "--":
            ended = True
        elif not ended and a.startswith("--") and len(a) > 2:
            flags.add(a[2:].split("=", 1)[0])
        elif not ended and a.startswith("-") and len(a) > 1:
            flags.update(a[1:])
        else:
            words.append(a)
            ended = ended or stops_at_operand
    return flags, words
