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

What this sweep can and cannot see, because a denominator you cannot check is
worse than no denominator: it follows a reference only when the doc names a
source file whose extension is in CODE_EXT below, and it reads every markdown
file in the tree except vendored and build directories. Dates are day-granular,
so a doc and its code changed on the same day cannot be ordered. All three
limits are reported in the output, with counts, and a zero is always labelled
with which of them it belongs to.

Usage: staleness_sweep.py <repo>
"""
import os
import re
import subprocess
import sys

# One source of truth for which references the sweep can follow. The backtick
# pattern is derived from it, because keeping two lists in sync by hand is the
# failure this skill is about: the previous version listed .tsx here and not in
# the pattern, so a doc naming a .tsx file was silently unmatched.
CODE_EXT = {
    ".rs", ".go", ".java", ".kt", ".swift", ".cs", ".rb", ".php",
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".py", ".c", ".h", ".cpp", ".hpp", ".sql", ".toml", ".sh",
}

# Directories whose markdown is somebody else's. Everything else is a doc.
SKIP_DIRS = {
    ".git", "node_modules", "target", "vendor", "third_party", "dist", "build",
    ".venv", "venv", "site-packages", "__pycache__", ".next", ".cache", ".tox",
}

RE_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
RE_BACKTICK_PATH = re.compile(
    r"`([\w./-]+\.(?:%s))`" % "|".join(sorted(e.lstrip(".") for e in CODE_EXT)))


def source_extensions(repo):
    """Source-looking extensions present in the repo, most frequent first.

    Used to tell two very different zeros apart: "the docs are in sync" and
    "this sweep cannot read this codebase's language".
    """
    ignore = {".md", ".txt", ".json", ".yml", ".yaml", ".lock", ".toml",
              ".cfg", ".ini", ".svg", ".png", ".jpg", ".gitignore", ""}
    counts = {}
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in ignore:
                counts[ext] = counts.get(ext, 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


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

    # Every markdown file in the tree is a doc. The previous version kept only
    # docs/, .claude/ and the root, which was this author's repo layout mistaken
    # for a general one: on a plugin repo it silently dropped 5 of 6 docs and
    # still printed a denominator, which is the exact failure this sweep warns
    # about. Skipped directories are counted and named in the output instead.
    docs, skipped = [], {}
    for dirpath, dirnames, filenames in os.walk(repo):
        for d in list(dirnames):
            if d in SKIP_DIRS:
                dirnames.remove(d)
                if d != ".git":
                    n = sum(len([f for f in fs if f.endswith(".md")])
                            for _, _, fs in os.walk(os.path.join(dirpath, d)))
                    if n:
                        skipped[d] = skipped.get(d, 0) + n
        for fn in filenames:
            if fn.endswith(".md"):
                docs.append(os.path.relpath(os.path.join(dirpath, fn), repo).replace(os.sep, "/"))

    if skipped:
        detail = ", ".join("%s (%d)" % (d, n) for d, n in sorted(skipped.items()))
        print("markdown skipped as vendored or build output: %d in %s"
              % (sum(skipped.values()), detail))

    stale, plans, no_refs, same_day = [], [], [], []
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
        elif code_last and d_last == code_last:
            # Dates here are day-granular. A doc and its code last touched on
            # the same day cannot be ordered, and calling that clean would be
            # the denominator failure again, one level down.
            same_day.append(doc)
        if code_first and d_first < code_first:
            plans.append((doc, d_first, code_first))

    print(f"docs examined: {len(docs)}   with code references: {len(docs) - len(no_refs)}")
    print(f"  -> {len(no_refs)} reference no source file, so this sweep cannot judge them")

    # Three zeros that print alike and mean different things.
    if not docs:
        print("  NOT APPLICABLE: no markdown found outside vendored directories, so\n"
              "  there is no documentation for this sweep to judge. That is itself\n"
              "  worth reporting: it is a finding about the repo, not a clean result.")
    elif len(no_refs) == len(docs):
        exts = source_extensions(repo)
        covered = [e for e, _ in exts if e in CODE_EXT]
        top = ", ".join("%s x%d" % (e, n) for e, n in exts[:5]) or "none found"
        if not covered:
            print("  NOT APPLICABLE: no doc could be judged, and this codebase's\n"
                  "  languages are ones this sweep cannot follow. Extensions present:\n"
                  "  %s.\n"
                  "  A zero here means nothing was read, not that the docs are current.\n"
                  "  Compare docs against code by reading, or add the extension to\n"
                  "  CODE_EXT if references to it are followable." % top)
        else:
            print("  The sweep can read %s in this repo, so the zero is about how the\n"
                  "  docs are written: none of them name a source file. Referencing\n"
                  "  files by path is what makes this check possible at all."
                  % ", ".join(covered))
    print()

    if same_day:
        print(f"UNRESOLVED — {len(same_day)} doc/code pairs last changed on the same\n"
              f"  day, which day-granular dates cannot order. Not clean, not stale:\n"
              f"  {', '.join(sorted(same_day)[:6])}"
              + ("" if len(same_day) <= 6 else f" (+{len(same_day) - 6} more)") + "\n")

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
