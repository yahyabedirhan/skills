"""Shell command text -> the simple commands it runs, and whether a command row covers one.

The pre-tool hook reads a command the way the shell would run it, not as text,
so a rule catches the common spellings of the same command:

- quoting is read first: single quotes, `\\` escapes, comments and `$(( ))` hold
  text, not commands; `$(…)` and backticks outside single quotes are read as
  commands of their own, and so is a heredoc body when its delimiter is unquoted;
- compound commands are split on `&&`, `||`, `;`, `|`, `&`, newlines and parentheses;
- leading `VAR=value` words, shell keywords (`then`, `do`, `{`, `!`) and
  wrappers (`timeout`, `nice`, `setsid`, `env`, `xargs`, `watch`, `flock`, …) are
  dropped; a wrapper that runs no command is read as itself alone (`env -u X` -> `env`);
- a program named by path (`/bin/rm`) is read by its basename, in lower case where
  the filesystem ignores case (macOS runs `/bin/rm` for `RM`; Linux finds no `RM`);
- the command inside `<shell> -c '…'` (any flag cluster holding `c`, such as
  `-lc`), `eval`, `sudo`, `find -exec`, a heredoc or a pipe into a shell is read
  as a command of its own;
- flags are read anywhere after the program (`git push origin main --force`,
  `rm x -rf`), clustered or not (`-rfv`), until `--`; `find`'s one-dash words
  (`-delete`) are flags by name;
- redirect targets are files the command reads (`< x`) or writes (`> x`, `>> x`,
  `&> x`), and `tee`'s operands files it writes (tee_writes).

What it can't see (a glob the shell expands, a variable holding a command, a
script file's contents) is named as a gap in the rule table.

Standard library only: it runs on macOS's Python 3.9.
"""
from __future__ import annotations

import fnmatch
import os
import re
import shlex
import sys

# Whether program names are read case-insensitively: macOS's and Windows's default
# filesystems find `/bin/rm` for `RM`, Linux's don't.
FOLD_CASE = sys.platform in ("darwin", "win32")
SHELLS = {"bash", "sh", "zsh", "dash", "ksh", "fish", "ash", "mksh", "csh", "tcsh"}
# Shell options that take the next word as their value.
SHELL_VALUE_OPTIONS = {"-o", "+o", "-O", "+O", "--rcfile", "--init-file"}
# Programs whose one-dash words are whole option names (`find -delete`), not letter clusters.
WORD_OPTIONS = {"find"}
# Words that start a command without being its program.
KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "{", "}"}
# Wrappers run the command after their own options; the value each option takes is skipped.
WRAPPERS = {
    "arch": {"-arch", "-e", "-d"},
    "builtin": set(),
    "busybox": set(),
    "caffeinate": {"-t", "-w"},
    "chronic": set(),
    "command": set(),
    "doas": {"-u", "-C"},
    "env": {"-u", "-C", "-P", "--unset", "--chdir"},
    "exec": {"-a"},
    "flock": {"-w", "--wait", "--timeout", "-E", "--conflict-exit-code"},
    "ionice": {"-c", "-n", "-p"},
    "nice": {"-n", "--adjustment"},
    "nohup": set(),
    "noglob": set(),
    "parallel": {"-j", "--jobs", "-S", "--sshlogin", "-a", "--arg-file", "-d", "--delimiter", "-I", "--colsep",
                 "-C", "-N", "-n", "--max-args", "-L", "--max-lines", "--joblog", "--results", "--tmpdir",
                 "--workdir", "--env", "--timeout", "--delay"},
    "script": {"-F", "-t", "-T", "-I", "-O", "-B", "-E", "-m", "--log-io", "--log-in", "--log-out",
               "--log-timing", "--echo", "--logging-format"},
    "setsid": set(),
    "stdbuf": {"-i", "-o", "-e"},
    "sudo": {"-u", "-g", "-C", "-D", "-h", "-p", "-r", "-t", "-U", "-T", "-R"},
    "time": {"-o", "-f"},
    "timeout": {"-s", "-k", "--signal", "--kill-after"},
    "unbuffer": set(),
    "watch": {"-n", "--interval", "-q", "--equexit"},
    "xargs": {"-I", "-J", "-L", "-n", "-P", "-d", "-s", "-E", "-a", "-R", "-S", "--delimiter", "--max-args",
              "--max-procs", "--arg-file", "--replace", "--max-lines", "--eof", "--max-chars"},
}
# Wrappers whose first word after the options is theirs, not the command's.
WRAPPER_POSITIONALS = {"timeout": 1, "flock": 1, "script": 1}
# Wrappers whose option takes a whole shell string (`flock f -c '…'`, `script -c '…'`).
SHELL_STRING_OPTIONS = {"flock": {"-c", "--command"}, "script": {"-c", "--command"}}
# Wrappers that run their command words joined as one shell string (`watch 'rm -rf x'`).
JOINS_WORDS = {"watch", "parallel"}
# Where parallel's command ends and its argument lists start.
PARALLEL_INPUTS = {":::", "::::", ":::+", "::::+"}
# Options that make `command` look a name up instead of running it.
LOOKUP_ONLY = {"command": {"-v", "-V"}}
FIND_EXEC = {"-exec", "-execdir", "-ok", "-okdir"}

PUNCTUATION = "();<>|&\n`"
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\+?=")
FEEDS_A_SHELL = re.compile(r"(^|[\s|;&(`])(\S*/)?(" + "|".join(sorted(SHELLS | {"eval", "source"})) + r")(\s|$)")
# Characters that end a word, after which `#` starts a comment.
WORD_BREAKS = " \t\r\n;&|()<>"
MAX_DEPTH = 8


def simple_commands(text: str, depth: int = 0, files=None) -> list:
    """Every simple command the text runs, as argv lists with the program as a basename.

    With a `files` list, the files its redirects name are appended to it as (path, access)."""
    if depth > MAX_DEPTH or not text.strip():
        return []
    text = text.replace("\\\n", "")
    scan = _Scanner(text)
    out = []
    for inner in scan.shell_bodies + scan.substitutions:
        out += simple_commands(inner, depth + 1, files)
    segments = []  # (words, the separator before them)
    words, before, redirect = [], "", None
    for token in _tokens(scan.kept) + [";"]:
        if _is_punctuation(token):
            if "<" in token or ">" in token:
                redirect = token
                continue
            if words:
                segments.append((words, before))
            words, before, redirect = [], token, None
            continue
        if redirect is not None:
            if redirect == "<<<" and any(_program(w) in SHELLS for w in words):
                out += simple_commands(token, depth + 1, files)  # a here-string fed to a shell
            access = _redirect_access(redirect, token)
            if access and files is not None:
                files.append((token, access))
            redirect = None
            continue
        words.append(token)
    for i, (words, before) in enumerate(segments):
        for argv in _unwrap(words, depth, files):
            out.append(argv)
            if before in ("|", "|&") and _reads_stdin_as_shell(argv) and i:
                fed = _strip(segments[i - 1][0])[0][1:]  # the words the command before the pipe prints
                for text in [" ".join(fed)] + fed:  # `echo rm -rf x | sh`, `printf 'rm -rf x' | sh`
                    out += simple_commands(text, depth + 1, files)
    return out


def tee_writes(argvs: list) -> list:
    """The files `tee` writes among these simple commands, as (path, "write") pairs."""
    return [(a, "write") for argv in argvs if argv[0] == "tee" for a in argv[1:] if a and not a.startswith("-")]


def _redirect_access(redirect: str, target: str):
    """`read` or `write` for a redirect to a file; None for a heredoc, a here-string or a descriptor (`>&2`)."""
    if redirect.startswith("<<"):
        return None
    if redirect.endswith("&") and (target.isdigit() or target == "-"):
        return None
    return "write" if ">" in redirect else "read"


def _tokens(text: str) -> list:
    lexer = shlex.shlex(text, posix=True, punctuation_chars=PUNCTUATION)
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = ""  # the scanner already dropped comments
    try:
        return list(lexer)
    except ValueError:  # an unclosed quote: read the words without quoting
        return re.findall(r"[^\s;&|()<>'\"]+|[;&|()\n]+|[<>]+", text)


def _is_punctuation(token: str) -> bool:
    return bool(token) and all(c in PUNCTUATION for c in token)


class _Scanner:
    """One pass over shell text that reads its quoting the way the shell does.

    - `kept`: the text without comments and heredoc bodies, for the tokenizer;
    - `substitutions`: the text inside each `$(…)`, backticks and `$(( ))` outside
      single quotes, and inside an unquoted heredoc's body, to be read as commands;
    - `shell_bodies`: heredoc bodies on a line that feeds a shell (`bash <<EOF`).

    A `<<` counts as a heredoc only where the shell reads code: never inside
    quotes, a comment or `$(( ))`.
    """

    def __init__(self, text: str, heredoc_body: bool = False):
        self.text, self.kept, self.substitutions, self.shell_bodies = text, [], [], []
        self.pending = []  # heredocs waiting for the end of their line: (delimiter, strip tabs, expands, line start)
        if heredoc_body:
            self._quoted(0, None)
        else:
            self._code(0, None)
        self.kept = "".join(self.kept)

    def _emit(self, i: int, j: int) -> int:
        self.kept.append(self.text[i:j])
        return j

    def _code(self, i: int, closer):
        """Code up to `closer` (`)` for `$(`, a backtick, or None for the end); returns the index after it."""
        t, depth, word_start = self.text, 0, True
        while i < len(t):
            c = t[i]
            if c == "\\":
                i, word_start = self._emit(i, i + 2), False
            elif c == closer and (closer == "`" or depth == 0):
                return self._emit(i, i + 1)
            elif c == "\n":
                i, word_start = self._heredoc_bodies(self._emit(i, i + 1)), True
            elif c == "#" and word_start:
                end = t.find("\n", i)
                i = len(t) if end == -1 else end
            elif c == "'" or t.startswith("$'", i):
                i, word_start = self._single(i), False
            elif c == '"':
                i, word_start = self._quoted(self._emit(i, i + 1), '"'), False
            elif t.startswith("$((", i):
                i, word_start = self._arithmetic(i), False
            elif t.startswith("$(", i) or c == "`":
                i, word_start = self._substitution(i), False
            elif t.startswith("<<", i) and not t.startswith("<<<", i) and t[i - 1:i] != "<":
                i, word_start = self._heredoc_marker(i), False
            else:
                depth += (c == "(") - (c == ")" and depth > 0)
                i, word_start = self._emit(i, i + 1), c in WORD_BREAKS
        return i

    def _single(self, i: int) -> int:
        """A single-quoted string, or `$'…'`, where a backslash escapes."""
        t = self.text
        j, escapes = (i + 2, True) if t[i] == "$" else (i + 1, False)
        while j < len(t) and t[j] != "'":
            j += 2 if escapes and t[j] == "\\" else 1
        return self._emit(i, min(j + 1, len(t)))

    def _quoted(self, i: int, closer) -> int:
        """Double-quoted text (closer `"`), or a heredoc body (None): only `$(…)`, backticks and `$(( ))` run."""
        t = self.text
        while i < len(t):
            c = t[i]
            if c == "\\":
                i = self._emit(i, i + 2)
            elif c == closer:
                return self._emit(i, i + 1)
            elif t.startswith("$((", i):
                i = self._arithmetic(i)
            elif t.startswith("$(", i) or c == "`":
                i = self._substitution(i)
            else:
                i = self._emit(i, i + 1)
        return i

    def _substitution(self, i: int) -> int:
        opener = 2 if self.text[i] == "$" else 1
        start = self._emit(i, i + opener)
        end = self._code(start, ")" if opener == 2 else "`")
        closed = end > start and self.text[end - 1] == (")" if opener == 2 else "`")
        self.substitutions.append(self.text[start:end - 1] if closed else self.text[start:end])
        return end

    def _arithmetic(self, i: int) -> int:
        """`$(( ))`: arithmetic, where `<<` is a shift. Its text is still read as a command, in case it isn't."""
        t, j, depth = self.text, i + 3, 0
        while j < len(t) and not (depth == 0 and t.startswith("))", j)):
            depth += (t[j] == "(") - (t[j] == ")")
            j += 1
        self.substitutions.append(t[i + 3:j])
        return self._emit(i, min(j + 2, len(t)))

    def _heredoc_marker(self, i: int) -> int:
        """`<<EOF`, `<<-'EOF'`, `<< "EOF"`: note the heredoc, whose body starts after this line."""
        t, j = self.text, i + 2
        strip_tabs = t.startswith("-", j)
        j += strip_tabs
        while j < len(t) and t[j] in " \t":
            j += 1
        delimiter, quoted = [], False
        while j < len(t) and t[j] not in WORD_BREAKS:
            if t[j] in "'\"":
                end = t.find(t[j], j + 1)
                end = len(t) if end == -1 else end
                delimiter.append(t[j + 1:end])
                j, quoted = end + 1, True
            elif t[j] == "\\":
                delimiter.append(t[j + 1:j + 2])
                j, quoted = j + 2, True
            else:
                delimiter.append(t[j])
                j += 1
        if delimiter:
            self.pending.append(("".join(delimiter), strip_tabs, not quoted, t.rfind("\n", 0, i) + 1))
        return self._emit(i, j)

    def _heredoc_bodies(self, i: int) -> int:
        """At the end of a line: skip the body of each heredoc it started; returns where the code goes on."""
        t, pending, self.pending = self.text, self.pending, []
        for delimiter, strip_tabs, expands, line_start in pending:
            body_start = i
            while i < len(t):
                end = t.find("\n", i)
                end = len(t) if end == -1 else end
                line, body_end, i = t[i:end], i, end + 1
                if (line.lstrip("\t") if strip_tabs else line) == delimiter:
                    break
            else:
                body_end = len(t)
            body = t[body_start:body_end]
            if expands:  # an unquoted delimiter: `$(…)` in the body runs
                self.substitutions += _Scanner(body, heredoc_body=True).substitutions
            if FEEDS_A_SHELL.search(t[line_start:body_start]):
                self.shell_bodies.append(body)
        return min(i, len(t))


def _unwrap(words: list, depth: int, files=None) -> list:
    """The command itself, then every command it runs inside it."""
    argv, texts = _strip(words)
    out = [argv] if argv else []
    for text in texts:
        out += simple_commands(text, depth + 1, files)
    if not argv:
        return out
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
        out += simple_commands(inner_text, depth + 1, files)
    if inner_argv:
        out += _unwrap(inner_argv, depth + 1, files)
    return out


def _strip(words: list):
    """Drop assignments, keywords and wrappers; the program becomes its basename (see _program).

    Returns the argv, and the shell strings a wrapper runs (`flock f -c '…'`, `watch 'rm -rf x'`)."""
    i, texts = 0, []
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
                return [], texts
            shell_string = _option_value(rest, SHELL_STRING_OPTIONS.get(name, ()))
            if shell_string is not None:
                return [name], texts + [shell_string]
            rest = _after_options(rest, WRAPPERS[name])
            rest = rest[WRAPPER_POSITIONALS.get(name, 0):]
            if name == "parallel":
                rest = rest[:next((k for k, a in enumerate(rest) if a in PARALLEL_INPUTS), len(rest))]
                words = words[:len(words) - len(words[i + 1:])] + rest
            if name in JOINS_WORDS and rest:
                texts.append(" ".join(rest))
            if not rest:
                return [name], texts  # a wrapper that runs nothing does its own job: `env -u X` prints the environment
            i = len(words) - len(rest)
        else:
            break
    argv = words[i:]
    if not argv:
        return [], texts
    return [_program(argv[0]) or argv[0], *argv[1:]], texts


def _option_value(args: list, options) -> object:
    """The value of the first of these options (`-c '…'`, `--command=…`) among a wrapper's arguments, or None."""
    for k, a in enumerate(args):
        if a in options and k + 1 < len(args):
            return args[k + 1]
        name, eq, value = a.partition("=")
        if eq and name in options:
            return value
    return None


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
        if a == "--command":  # fish
            return args[i + 1] if i + 1 < len(args) else None
        if a.startswith("--command="):
            return a.split("=", 1)[1]
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


# Marks a `$` the shell expands, so a word keeps whether it names a variable once quotes are gone.
EXPANDS = "\x01"
_EXPANSION = re.compile(EXPANDS + r"(?:\{(?!#)([A-Za-z_][A-Za-z0-9_]*)|([A-Za-z_][A-Za-z0-9_]*))")


def mark_expansions(text: str) -> str:
    """The text with each `$NAME` and `${NAME…}` the shell would expand marked by EXPANDS.

    Single quotes, `$'…'` and a backslash keep a `$` literal; double quotes don't.
    """
    out, i, quoted = [], 0, False
    while i < len(text):
        c = text[i]
        if c == "\\":
            out.append(text[i:i + 2])
            i += 2
            continue
        if not quoted and (c == "'" or text.startswith("$'", i)):
            j = text.find("'", i + (2 if c == "$" else 1))
            j = len(text) if j == -1 else j + 1
            out.append(text[i:j])
            i = j
            continue
        if c == '"':
            quoted = not quoted
        elif c == "$" and re.match(r"[A-Za-z_{]", text[i + 1:i + 2]):
            c = EXPANDS
        out.append(c)
        i += 1
    return "".join(out)


def expanded_variables(argv: list) -> list:
    """The variable names a marked argv expands in its arguments (not `${#NAME}`, which is a length)."""
    return [a or b for word in argv[1:] for a, b in _EXPANSION.findall(word)]


def program_matches(rule, program: str) -> bool:
    """`mkfs` covers `mkfs.ext4`: a program's dotted variants are the same program."""
    return any(program == p or program.startswith(p + ".") for p in rule.programs)


def covers(rule, argv: list) -> bool:
    """Whether a command row covers this normalised argv, whatever the flag order or position."""
    if not argv or not program_matches(rule, argv[0]):
        return False
    if rule.flags_only:  # `declare -x`: only flags, which list what carries them
        return len(argv) > 1 and all(a[:1] in ("-", "+") and len(a) > 1 for a in argv[1:])
    if rule.bare:
        return len(argv) == 1
    if rule.variables:  # a marked argv: see mark_expansions
        return any(fnmatch.fnmatchcase(name.upper(), glob.upper())
                   for name in expanded_variables(argv) for glob in rule.variables)
    flags, words = _flags_and_words(argv)
    if not all(any(name in flags for name in group) for group in rule.flags):
        return False
    for sub in rule.subcommands:
        for start in range(len(words) - len(sub) + 1):
            if tuple(words[start:start + len(sub)]) != sub:
                continue
            after = words[start + len(sub):]
            if rule.any_operand:
                if any(w in rule.any_operand for w in after):
                    return True
            elif any(tuple(after[:len(o)]) == o for o in rule.operands):
                return True
    return False


def _flags_and_words(argv: list):
    """Flag names (short letters and long names) and the other words, read past operands until `--`.

    A shell's own options end at its first operand; after that the words are
    its script's arguments.
    """
    flags, words, ended = set(), [], False
    stops_at_operand = argv[0] in SHELLS
    word_options = argv[0] in WORD_OPTIONS
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
            flags.update([a[1:]] if word_options else a[1:])
        else:
            words.append(a)
            ended = ended or stops_at_operand
    return flags, words
