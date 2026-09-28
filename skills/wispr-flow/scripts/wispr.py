#!/usr/bin/env python3
"""Read Wispr Flow's dictation history and read or change its dictionary.

Wispr Flow (macOS) keeps its data in a local SQLite database. This script is
the only thing that touches it: every read opens it read-only, and every write
backs up the dictionary first and records a batch id that `dict undo` reverts.

Run `wispr.py <command> --help` for each command's options.
"""

import argparse
import datetime as dt
import json
import os
import re
import sqlite3
import subprocess
import sys
import uuid

DEFAULT_DB = os.path.expanduser("~/Library/Application Support/Wispr Flow/flow.sqlite")
DEFAULT_BACKUP_DIR = os.path.join(
    os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state")), "wispr-flow", "backups"
)
PERSONAL_DICTIONARY = "00000000-0000-0000-0000-000000000000"
BATCH_SOURCE = "manual"

# Columns this script relies on. `status` fails loudly when an app update drops one.
EXPECTED = {
    "History": ["transcriptEntityId", "asrText", "formattedText", "editedText", "timestamp", "app", "numWords"],
    "Dictionary": ["id", "phrase", "replacement", "teamDictionaryId", "manualEntry", "createdAt",
                   "modifiedAt", "isDeleted", "source", "isSnippet", "isStarred", "frequencyUsed",
                   "remoteFrequencyUsed", "observedSource", "lastUsed"],
}


# ---------- time ----------

def parse_duration(text):
    """'30m', '3h', '2d', '1h30m', '90s', '1w' -> timedelta."""
    parts = re.findall(r"(\d+(?:\.\d+)?)\s*([smhdw])", text.strip().lower())
    if not parts or "".join(n + u for n, u in parts) != re.sub(r"\s+", "", text.strip().lower()):
        raise argparse.ArgumentTypeError(f"bad duration {text!r}; use forms like 30m, 3h, 2d, 1h30m")
    unit = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days", "w": "weeks"}
    return sum((dt.timedelta(**{unit[u]: float(n)}) for n, u in parts), dt.timedelta())


def parse_when(text):
    """ISO date or datetime; a value without a zone is local time."""
    value = dt.datetime.fromisoformat(text)
    if value.tzinfo is None:
        value = value.astimezone()
    return value


def db_time(value):
    """datetime -> the database's text format, e.g. '2026-09-28 08:36:09.348 +00:00'."""
    return value.astimezone(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " +00:00"


def now_db():
    return db_time(dt.datetime.now(dt.timezone.utc))


def local(ts):
    """Database timestamp -> local 'YYYY-MM-DD HH:MM'."""
    if not ts:
        return ""
    value = dt.datetime.strptime(ts[:23], "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=dt.timezone.utc)
    return value.astimezone().strftime("%Y-%m-%d %H:%M")


def time_window(args):
    """--since/--from/--to -> (lower, upper) database timestamps; either may be None."""
    lower = upper = None
    if getattr(args, "since", None):
        lower = db_time(dt.datetime.now(dt.timezone.utc) - args.since)
    if getattr(args, "start", None):
        lower = db_time(args.start)
    if getattr(args, "end", None):
        upper = db_time(args.end)
    return lower, upper


# ---------- database ----------

def connect(args, write=False):
    if not os.path.exists(args.db):
        sys.exit(f"Wispr Flow database not found at {args.db}. Is Wispr Flow installed?")
    if write:
        return sqlite3.connect(args.db, timeout=15)
    return sqlite3.connect(f"file:{args.db}?mode=ro", uri=True, timeout=15)


def rows(con, sql, params=()):
    con.row_factory = sqlite3.Row
    return [dict(r) for r in con.execute(sql, params)]


def app_running():
    out = subprocess.run(["pgrep", "-f", "Wispr Flow.app/Contents/MacOS/Wispr Flow"],
                         capture_output=True, text=True)
    return out.returncode == 0


def emit(data, fmt):
    if fmt == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif fmt == "jsonl":
        for item in data:
            print(json.dumps(item, ensure_ascii=False))


def norm(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


# ---------- history ----------

def history_query(con, args):
    lower, upper = time_window(args)
    where, params = [], []
    if lower:
        where.append("timestamp >= ?"); params.append(lower)
    if upper:
        where.append("timestamp < ?"); params.append(upper)
    if not args.include_empty:
        where.append("coalesce(trim(formattedText), '') <> ''")
    if args.app:
        where.append("app like ?"); params.append(f"%{args.app}%")
    if args.grep:
        where.append("(asrText like ? or formattedText like ?)")
        params += [f"%{args.grep}%"] * 2
    sql = ("select transcriptEntityId as id, timestamp, app, asrText as raw, formattedText as formatted, "
           "editedText as edited, numWords as words from History")
    if where:
        sql += " where " + " and ".join(where)
    sql += " order by timestamp " + ("desc" if args.newest_first else "asc")
    if args.limit:
        sql += f" limit {int(args.limit)}"
    return rows(con, sql, params)


def cmd_history(args):
    con = connect(args)
    items = history_query(con, args)
    fields = [f.strip() for f in args.fields.split(",")]
    for item in items:
        item["local_time"] = local(item["timestamp"])
        # An "edit" equal to the formatted text is not an edit; drop it so real edits stand out.
        if norm(item["edited"]) == norm(item["formatted"]):
            item["edited"] = None
    if args.format in ("json", "jsonl"):
        emit([{k: i[k] for k in ["id", "timestamp", "local_time", "app", "words"] + fields if k in i}
              for i in items], args.format)
        return
    for i in items:
        print(f"### {i['local_time']} | {i['app'] or '-'} | {i['words'] or 0} words")
        for field in fields:
            value = i.get(field)
            if value and not (field == "raw" and "formatted" in fields and norm(value) == norm(i["formatted"])):
                print(f"{field.upper()}: {value}")
        print()
    print(f"-- {len(items)} dictations", file=sys.stderr)


def cmd_count(args):
    """How many dictations contain each term, in the raw or formatted text."""
    con = connect(args)
    args.include_empty = False
    args.grep = None
    args.newest_first = False
    args.limit = None
    items = history_query(con, args)
    result = []
    for term in args.terms:
        pattern = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.IGNORECASE)
        hits = [i for i in items if pattern.search(i["raw"] or "") or pattern.search(i["formatted"] or "")]
        example = ""
        if hits:
            text = hits[-1]["formatted"] or hits[-1]["raw"]
            m = pattern.search(text) or pattern.search(hits[-1]["raw"] or "")
            src = text if pattern.search(text) else hits[-1]["raw"]
            start = max(0, m.start() - 40)
            example = norm(src[start:m.end() + 40])
        result.append({"term": term, "dictations": len(hits), "example": example})
    if args.format == "json":
        emit(result, "json")
        return
    print("| Term | Dictations | Example |\n|---|---|---|")
    for r in result:
        print(f"| {r['term']} | {r['dictations']} | {r['example'].replace('|', '/')} |")


# ---------- dictionary ----------

def active_entries(con, include_deleted=False):
    sql = ("select id, phrase, replacement, source, observedSource, manualEntry, isSnippet, isDeleted, "
           "frequencyUsed, lastUsed, createdAt, modifiedAt from Dictionary where teamDictionaryId = ?")
    if not include_deleted:
        sql += " and isDeleted = 0"
    return rows(con, sql + " order by lower(phrase)", (PERSONAL_DICTIONARY,))


def cmd_dict_list(args):
    con = connect(args)
    items = active_entries(con, args.deleted)
    if args.search:
        s = args.search.lower()
        items = [i for i in items if s in i["phrase"].lower() or s in (i["replacement"] or "").lower()]
    if args.kind == "rules":
        items = [i for i in items if i["replacement"] and not i["isSnippet"]]
    elif args.kind == "words":
        items = [i for i in items if not i["replacement"]]
    elif args.kind == "snippets":
        items = [i for i in items if i["isSnippet"] or (i["replacement"] and len(i["replacement"]) > 60)]
    if args.format in ("json", "jsonl"):
        emit(items, args.format)
        return
    print("| Phrase | Replacement | Source | Used | Added |\n|---|---|---|---|---|")
    for i in items:
        repl = (i["replacement"] or "").replace("\n", " ")
        repl = repl[:57] + "..." if len(repl) > 60 else repl
        src = i["source"] or ""
        if i["observedSource"]:
            src += f" (heard: {i['observedSource']})"
        if i["isDeleted"]:
            src += ", deleted"
        print(f"| {i['phrase']} | {repl} | {src} | {i['frequencyUsed']} | {local(i['createdAt'])[:10]} |")
    print(f"-- {len(items)} entries", file=sys.stderr)


def backup(con, backup_dir, label):
    os.makedirs(backup_dir, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(backup_dir, f"dictionary-{stamp}-{label}.json")
    data = rows(con, "select * from Dictionary")
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    return path, len(data)


def load_entries(args):
    """Entries from --file (JSON list of {phrase, replacement?}) or from the positional phrase."""
    if args.file:
        with open(args.file) as fh:
            data = json.load(fh)
        return [{"phrase": e["phrase"].strip(), "replacement": (e.get("replacement") or None)} for e in data]
    if not args.phrase:
        sys.exit("give a PHRASE or --file")
    return [{"phrase": args.phrase.strip(), "replacement": args.replace}]


def cmd_dict_add(args):
    entries = load_entries(args)
    con = connect(args, write=not args.dry_run)
    existing = {i["phrase"].lower(): i for i in active_entries(con)}
    deleted = {i["phrase"]: i for i in active_entries(con, True) if i["isDeleted"]}
    plan = []
    for e in entries:
        hit = existing.get(e["phrase"].lower())
        if hit and (hit["replacement"] or None) == e["replacement"]:
            plan.append((e, "skip: already present"))
        elif hit:
            plan.append((e, f"skip: exists with replacement {hit['replacement']!r}; remove it first"))
        elif e["phrase"] in deleted:
            plan.append((e, "revive deleted entry"))
        else:
            plan.append((e, "add"))
    print("| Phrase | Replacement | Action |\n|---|---|---|")
    for e, action in plan:
        print(f"| {e['phrase']} | {e['replacement'] or ''} | {action} |")
    todo = [(e, a) for e, a in plan if not a.startswith("skip")]
    if args.dry_run or not todo:
        print(f"-- {'dry run, ' if args.dry_run else ''}{len(todo)} to write", file=sys.stderr)
        return
    path, n = backup(con, args.backup_dir, "before-add")
    batch = now_db()
    with con:
        for e, action in todo:
            if action == "revive deleted entry":
                con.execute("update Dictionary set isDeleted=0, replacement=?, modifiedAt=?, createdAt=?, "
                            "source=?, manualEntry=1 where phrase=? and teamDictionaryId=?",
                            (e["replacement"], batch, batch, BATCH_SOURCE, e["phrase"], PERSONAL_DICTIONARY))
            else:
                con.execute(
                    "insert into Dictionary (id, phrase, replacement, teamDictionaryId, frequencyUsed, "
                    "remoteFrequencyUsed, manualEntry, createdAt, modifiedAt, isDeleted, source, isSnippet, "
                    "isStarred) values (?, ?, ?, ?, 0, 0, 1, ?, ?, 0, ?, 0, 0)",
                    (str(uuid.uuid4()), e["phrase"], e["replacement"], PERSONAL_DICTIONARY, batch, batch,
                     BATCH_SOURCE))
    print(f"-- wrote {len(todo)} entries; backup of {n} rows: {path}", file=sys.stderr)
    print(f"-- batch: {batch}  (revert with: dict undo --batch '{batch}')", file=sys.stderr)
    if app_running():
        print("-- Wispr Flow is running: restart it so it loads the new entries", file=sys.stderr)


def cmd_dict_remove(args):
    """Soft-delete (isDeleted=1), the way the app itself deletes an entry."""
    con = connect(args, write=not args.dry_run)
    phrases = args.phrases
    found = [i for i in active_entries(con) if i["phrase"].lower() in {p.lower() for p in phrases}]
    missing = sorted({p.lower() for p in phrases} - {i["phrase"].lower() for i in found})
    for i in found:
        print(f"remove: {i['phrase']}" + (f" -> {i['replacement']}" if i["replacement"] else ""))
    for p in missing:
        print(f"not found: {p}")
    if args.dry_run or not found:
        return
    path, n = backup(con, args.backup_dir, "before-remove")
    stamp = now_db()
    with con:
        con.executemany("update Dictionary set isDeleted=1, modifiedAt=? where id=?",
                        [(stamp, i["id"]) for i in found])
    print(f"-- removed {len(found)}; backup of {n} rows: {path}", file=sys.stderr)


def cmd_dict_undo(args):
    """Soft-delete every entry a `dict add` batch created."""
    con = connect(args, write=not args.dry_run)
    hits = rows(con, "select id, phrase, replacement from Dictionary where createdAt=? and isDeleted=0 "
                     "and teamDictionaryId=?", (args.batch, PERSONAL_DICTIONARY))
    for h in hits:
        print(f"undo: {h['phrase']}" + (f" -> {h['replacement']}" if h["replacement"] else ""))
    if args.dry_run or not hits:
        print(f"-- {len(hits)} entries in batch", file=sys.stderr)
        return
    path, n = backup(con, args.backup_dir, "before-undo")
    stamp = now_db()
    with con:
        con.executemany("update Dictionary set isDeleted=1, modifiedAt=? where id=?",
                        [(stamp, h["id"]) for h in hits])
    print(f"-- undid {len(hits)}; backup of {n} rows: {path}", file=sys.stderr)


def cmd_dict_backup(args):
    path, n = backup(connect(args), args.backup_dir, "manual")
    print(f"backed up {n} rows to {path}")


# ---------- status ----------

def cmd_status(args):
    con = connect(args)
    problems = []
    for table, cols in EXPECTED.items():
        have = {r[1] for r in con.execute(f"pragma table_info({table})")}
        miss = [c for c in cols if c not in have]
        if miss:
            problems.append(f"{table} is missing {', '.join(miss)}")
    info = rows(con, "select count(*) as dictations, min(timestamp) as first, max(timestamp) as last "
                     "from History where coalesce(trim(formattedText), '') <> ''")[0]
    d = rows(con, "select sum(isDeleted=0) as active, sum(isDeleted=0 and replacement is not null) as rules "
                  "from Dictionary where teamDictionaryId=?", (PERSONAL_DICTIONARY,))[0]
    print(f"database:   {args.db}")
    print(f"app:        {'running' if app_running() else 'not running'}")
    print(f"history:    {info['dictations']} dictations, {local(info['first'])} to {local(info['last'])}")
    print(f"dictionary: {d['active']} active entries, {d['rules']} with a replacement")
    print(f"backups:    {args.backup_dir}")
    print("schema:     " + ("ok" if not problems else "CHANGED: " + "; ".join(problems)))
    if problems:
        sys.exit(1)


# ---------- CLI ----------

def main():
    p = argparse.ArgumentParser(prog="wispr.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--db", default=os.environ.get("WISPR_FLOW_DB", DEFAULT_DB),
                   help="database path (env WISPR_FLOW_DB)")
    p.add_argument("--backup-dir", default=os.environ.get("WISPR_FLOW_BACKUP_DIR", DEFAULT_BACKUP_DIR),
                   help="where writes save a dictionary backup first (env WISPR_FLOW_BACKUP_DIR)")
    sub = p.add_subparsers(dest="command", required=True)

    def window(sp):
        sp.add_argument("--since", type=parse_duration, help="look back this far: 30m, 3h, 2d, 1h30m")
        sp.add_argument("--from", dest="start", type=parse_when, help="start, ISO date or datetime (local)")
        sp.add_argument("--to", dest="end", type=parse_when, help="end, ISO date or datetime (local)")
        sp.add_argument("--app", help="only dictations into apps whose bundle id contains this")

    sub.add_parser("status", help="database path, app state, counts, schema check").set_defaults(func=cmd_status)

    h = sub.add_parser("history", help="dictations in a time window")
    window(h)
    h.add_argument("--fields", default="formatted",
                   help="comma list of raw, formatted, edited (default: formatted); "
                        "raw is printed only where it differs from formatted")
    h.add_argument("--grep", help="only dictations whose text contains this")
    h.add_argument("--limit", type=int)
    h.add_argument("--newest-first", action="store_true")
    h.add_argument("--include-empty", action="store_true", help="keep empty dictations")
    h.add_argument("--format", choices=["text", "json", "jsonl"], default="text")
    h.set_defaults(func=cmd_history)

    c = sub.add_parser("count", help="how many dictations contain each term (whole word, any case)")
    window(c)
    c.add_argument("terms", nargs="+")
    c.add_argument("--format", choices=["table", "json"], default="table")
    c.set_defaults(func=cmd_count)

    d = sub.add_parser("dict", help="read or change the dictionary")
    dsub = d.add_subparsers(dest="dict_command", required=True)

    dl = dsub.add_parser("list", help="dictionary entries")
    dl.add_argument("--kind", choices=["all", "words", "rules", "snippets"], default="all")
    dl.add_argument("--search")
    dl.add_argument("--deleted", action="store_true", help="include deleted entries")
    dl.add_argument("--format", choices=["table", "json", "jsonl"], default="table")
    dl.set_defaults(func=cmd_dict_list)

    da = dsub.add_parser("add", help="add a word, or a rule with --replace; --file for a batch")
    da.add_argument("phrase", nargs="?", help="the word, or what Wispr mishears")
    da.add_argument("--replace", help="text to write instead of PHRASE")
    da.add_argument("--file", help='JSON list of {"phrase": ..., "replacement": ...}')
    da.add_argument("--dry-run", action="store_true")
    da.set_defaults(func=cmd_dict_add)

    dr = dsub.add_parser("remove", help="delete entries by phrase (soft delete, like the app)")
    dr.add_argument("phrases", nargs="+")
    dr.add_argument("--dry-run", action="store_true")
    dr.set_defaults(func=cmd_dict_remove)

    du = dsub.add_parser("undo", help="delete every entry one `dict add` batch created")
    du.add_argument("--batch", required=True, help="the batch timestamp `dict add` printed")
    du.add_argument("--dry-run", action="store_true")
    du.set_defaults(func=cmd_dict_undo)

    dsub.add_parser("backup", help="save the dictionary table as JSON").set_defaults(func=cmd_dict_backup)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
