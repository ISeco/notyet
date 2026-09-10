#!/usr/bin/env python3
"""Review sweep 3 — staleness by timestamp, plus the F10 first-commit check.

For each documentation file, find the source files it references and compare
commit dates two ways:

  LAST commit of the doc  vs  LAST commit of the code it describes
      -> the doc is older than its subject: a drift candidate.

  FIRST commit of the doc vs FIRST commit of the code it describes
      -> the doc predates its subject: it was written as a plan, not a
         description (F10), which needs a reconciliation pass rather than
         an update rule.

Needs full commit history. A shallow clone silently reports nonsense, so the
depth is checked and refused. Blobs are not needed — a `--filter=blob:none`
partial clone is enough, which is what makes this affordable on a large repo.

Usage: staleness_sweep.py <repo> [doc-glob ...]
"""
import os
import re
import subprocess
import sys

RE_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
RE_BACKTICK_PATH = re.compile(r"`([\w./-]+\.(?:rs|ts|py|go|java|sql|toml))`")
CODE_EXT = {".rs", ".ts", ".tsx", ".py", ".go", ".java", ".sql", ".toml"}


def git(repo, *args):
    try:
        r = subprocess.run(["git", "-C", repo, *args],
                           capture_output=True, text=True, timeout=60)
        return r.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return ""


def commit_dates(repo, path):
    """(first, last) author dates for a path, as ISO strings."""
    out = git(repo, "log", "--follow", "--format=%ad", "--date=short", "--", path)
    if not out:
        return None, None
    lines = out.splitlines()
    return lines[-1], lines[0]


def referenced_code(repo, doc_rel):
    """Source files the doc points at, as repo-relative paths that exist."""
    full = os.path.join(repo, doc_rel)
    try:
        body = open(full, encoding="utf-8", errors="replace").read()
    except OSError:
        return []
    cands = set()
    for m in list(RE_LINK.finditer(body)) + list(RE_BACKTICK_PATH.finditer(body)):
        raw = m.group(1).split("#")[0].strip()
        if not raw or raw.startswith(("http", "mailto:")):
            continue
        if os.path.splitext(raw)[1] not in CODE_EXT:
            continue
        for base in (os.path.dirname(doc_rel), ""):
            p = os.path.normpath(os.path.join(base, raw))
            if not p.startswith("..") and os.path.isfile(os.path.join(repo, p)):
                cands.add(p.replace(os.sep, "/"))
                break
    return sorted(cands)


USAGE = "usage: staleness_sweep.py <repo-path>"


def resolve_target():
    """Validate argv. Returns (path, exit_code); path is None when main should exit.

    This sweep already refuses a shallow clone, where the dates lie without
    erroring. An unreadable argument is the same class of problem: a zero that
    means "nothing was read" must never be printed as if it meant "clean".
    """
    args = sys.argv[1:]
    if not args or any(a in ("-h", "--help") for a in args):
        print(__doc__)
        return None, 0 if args else 2
    unknown = [a for a in args if a.startswith("-")]
    if unknown:
        sys.stderr.write("unknown option: %s\n%s\n" % (unknown[0], USAGE))
        return None, 2
    if len(args) != 1:
        sys.stderr.write("expected exactly one path, got %d\n%s\n"
                         % (len(args), USAGE))
        return None, 2
    repo = os.path.abspath(args[0])
    if not os.path.exists(repo):
        sys.stderr.write("no such path: %s\n" % repo)
        return None, 2
    if not os.path.isdir(repo):
        sys.stderr.write("not a directory: %s\n" % repo)
        return None, 2
    if not os.path.isdir(os.path.join(repo, ".git")):
        sys.stderr.write(
            "not a git repository: %s\n"
            "Both comparisons in this sweep are commit-date comparisons, so without "
            "history there is nothing to judge and a clean result would be a lie.\n"
            % repo)
        return None, 2
    return repo, 0


def main():
    repo, code = resolve_target()
    if repo is None:
        return code

    if os.path.isfile(os.path.join(repo, ".git", "shallow")):
        print("REFUSED: shallow clone — sweep 3 needs full history "
              "(git clone --filter=blob:none gives it cheaply).")
        return 1
    total = git(repo, "rev-list", "--count", "HEAD")
    print(f"history: {total} commits\n")

    docs = []
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in {".git", "node_modules", "target"}]
        for fn in filenames:
            if fn.endswith(".md"):
                docs.append(os.path.relpath(os.path.join(dirpath, fn), repo).replace(os.sep, "/"))
    docs = [d for d in docs if d.startswith(("docs/", ".claude/")) or "/" not in d]

    stale, plans, no_refs = [], [], []
    for doc in sorted(docs):
        refs = referenced_code(repo, doc)
        if not refs:
            no_refs.append(doc)
            continue
        d_first, d_last = commit_dates(repo, doc)
        if not d_last:
            continue
        code_first = code_last = None
        for r in refs:
            c_first, c_last = commit_dates(repo, r)
            if c_last and (code_last is None or c_last > code_last):
                code_last = c_last
            if c_first and (code_first is None or c_first < code_first):
                code_first = c_first
        if code_last and d_last < code_last:
            stale.append((doc, d_last, code_last, len(refs)))
        if code_first and d_first < code_first:
            plans.append((doc, d_first, code_first))

    print(f"docs examined: {len(docs)}   with code references: {len(docs) - len(no_refs)}")
    print(f"  -> {len(no_refs)} reference no source file, so this sweep cannot judge them\n")

    print(f"STALE — doc older than the code it describes ({len(stale)}):")
    for doc, d, c, n in sorted(stale, key=lambda x: x[1]):
        print(f"  doc {d}  code {c}  ({n} refs)  {doc}")
    if not stale:
        print("  none")

    print(f"\nF10 — doc predates its subject, written as a plan ({len(plans)}):")
    for doc, d, c in sorted(plans, key=lambda x: x[1]):
        print(f"  doc {d}  code {c}  {doc}")
    if not plans:
        print("  none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
