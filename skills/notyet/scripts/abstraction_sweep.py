#!/usr/bin/env python3
"""Abstraction sweep — the mechanical half of F5, in both directions.

Counts implementations of every declared abstraction boundary:

    0 implementations  -> promised and never built
    1 implementation   -> unearned (justified by a future that didn't arrive)
    2+ implementations -> earned, not reported

Also checks workspace members that are declared in configuration but absent
from disk, which is the same failure expressed in build config rather than
in source.

Reads only. Never installs, builds or executes anything in the target repo.

A boundary that is part of a library's PUBLIC API is reported separately:
a published interface with one internal implementation may exist for
consumers to implement, so counting it as unearned would be a false
positive. That distinction is the main threshold this script applies.

Usage: abstraction_sweep.py <repo-path> [--json]
"""
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

EXCLUDE_DIRS = {
    "node_modules", ".git", "target", "dist", "build", "out", ".next",
    "coverage", "vendor", "third_party", "zig-out", "zig-cache", ".venv",
    "__pycache__", "fixtures", "snapshots", "generated", ".turbo",
}

TS_EXT = {".ts", ".tsx", ".mts", ".cts"}
RUST_EXT = {".rs"}
TEST_HINT = re.compile(r"(^|[./_-])(test|tests|spec|__tests__|e2e)([./_-]|$)", re.I)

# --- declarations -----------------------------------------------------------
RE_TS_INTERFACE = re.compile(r"^\s*(export\s+)?(?:declare\s+)?interface\s+([A-Za-z_]\w*)")
RE_TS_ABSTRACT = re.compile(r"^\s*(export\s+)?(?:declare\s+)?abstract\s+class\s+([A-Za-z_]\w*)")
RE_RS_TRAIT = re.compile(r"^\s*(pub(?:\([^)]*\))?\s+)?(?:unsafe\s+)?(?:auto\s+)?trait\s+([A-Za-z_]\w*)")

# --- implementations --------------------------------------------------------
RE_TS_IMPLEMENTS = re.compile(r"\bimplements\s+([^{]+)")
RE_TS_EXTENDS = re.compile(r"\bclass\s+\w+(?:<[^>]*>)?\s+extends\s+([A-Za-z_][\w.]*)")
RE_TS_IFACE_EXTENDS = re.compile(r"^\s*(?:export\s+)?interface\s+\w+(?:<[^>]*>)?\s+extends\s+([^{]+)")
RE_NAME = re.compile(r"([A-Za-z_]\w*)")


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for fn in filenames:
            yield os.path.join(dirpath, fn)


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def rel(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")


RE_REEXPORT = re.compile(
    r"export\s+(?:type\s+)?(?:\*|\{[^}]*\})\s*(?:as\s+\w+\s*)?from\s+['\"]([^'\"]+)['\"]"
)


def public_api_files(root):
    """Files reachable from a package entry point by re-export.

    Checking only `index.ts` is not enough: a library commonly declares a
    public type in its own file and re-exports it from the entry point. Those
    types have exactly one implementation by design — the library's own — so
    without following the re-export chain they dominate the report as false
    positives. Reachability is what separates a published contract from an
    internal abstraction that never earned its keep.
    """
    entries = []
    for path in walk(root):
        r = rel(root, path)
        if os.path.basename(path) in {"index.ts", "index.tsx", "lib.rs", "mod.rs"}:
            entries.append(r)

    def resolve(from_file, spec):
        if not spec.startswith("."):
            return []
        base = os.path.normpath(os.path.join(os.path.dirname(from_file), spec))
        cands = [base + e for e in (".ts", ".tsx", ".mts", ".cts")]
        cands += [os.path.join(base, "index" + e) for e in (".ts", ".tsx")]
        return [c.replace(os.sep, "/") for c in cands
                if os.path.isfile(os.path.join(root, c))]

    seen, queue = set(entries), list(entries)
    while queue:
        cur = queue.pop()
        for m in RE_REEXPORT.finditer(read(os.path.join(root, cur))):
            for nxt in resolve(cur, m.group(1)):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
    return seen


def collect(root):
    decls = {}          # (lang, name) -> {"file","line","exported"}
    impls = defaultdict(set)   # (lang, name) -> {"file:line", ...}
    ts_files, rs_files = [], []

    for path in walk(root):
        ext = os.path.splitext(path)[1]
        if ext in TS_EXT:
            ts_files.append(path)
        elif ext in RUST_EXT:
            rs_files.append(path)

    for path in ts_files:
        r = rel(root, path)
        for i, line in enumerate(read(path).splitlines(), 1):
            for regex in (RE_TS_INTERFACE, RE_TS_ABSTRACT):
                m = regex.match(line)
                if m:
                    name = m.group(2)
                    key = ("ts", name)
                    if key not in decls:
                        decls[key] = {"file": r, "line": i, "exported": bool(m.group(1))}
            # `interface A extends B` composes types; it does not implement B.
            # Counting it flags every wire-format union member as unearned.
            for m in RE_TS_IMPLEMENTS.finditer(line):
                for nm in RE_NAME.findall(m.group(1)):
                    impls[("ts", nm)].add(f"{r}:{i}")
            for m in RE_TS_EXTENDS.finditer(line):
                impls[("ts", m.group(1).split(".")[-1])].add(f"{r}:{i}")

    for path in rs_files:
        r = rel(root, path)
        for i, line in enumerate(read(path).splitlines(), 1):
            m = RE_RS_TRAIT.match(line)
            if m:
                key = ("rs", m.group(2))
                if key not in decls:
                    decls[key] = {"file": r, "line": i, "exported": bool(m.group(1))}

    # Rust impls need whole-file scanning: `impl Trait for` can span lines.
    rs_blob = {}
    for path in rs_files:
        rs_blob[rel(root, path)] = read(path)
    for (lang, name), info in decls.items():
        if lang != "rs":
            continue
        pat = re.compile(
            r"impl\s*(?:<[^>]*>)?\s*(?:[\w:]+::)?" + re.escape(name) + r"\s*(?:<[^>]*>)?\s+for\s"
        )
        for r, blob in rs_blob.items():
            for m in pat.finditer(blob):
                line_no = blob.count("\n", 0, m.start()) + 1
                impls[(lang, name)].add(f"{r}:{line_no}")

    return decls, impls


def workspace_gaps(root):
    """Members declared in build config but absent from disk."""
    gaps = []

    cargo = os.path.join(root, "Cargo.toml")
    if os.path.isfile(cargo):
        blob = read(cargo)
        m = re.search(r"\[workspace\][^\[]*?members\s*=\s*\[(.*?)\]", blob, re.S)
        if m:
            for raw in re.findall(r'"([^"]+)"', m.group(1)):
                if "*" in raw:
                    continue
                if not os.path.isfile(os.path.join(root, raw, "Cargo.toml")):
                    gaps.append({"kind": "cargo-member", "declared": raw, "where": "Cargo.toml"})

    pnpm = os.path.join(root, "pnpm-workspace.yaml")
    globs = []
    if os.path.isfile(pnpm):
        # Only the `packages:` block lists workspace members. Modern
        # pnpm-workspace.yaml also carries unrelated sequences such as
        # onlyBuiltDependencies, and reading those as paths invents gaps.
        in_packages = False
        for line in read(pnpm).splitlines():
            if re.match(r"^\S", line):
                in_packages = line.startswith("packages:")
                continue
            if not in_packages:
                continue
            m = re.match(r"\s*-\s*['\"]?([^'\"#]+)['\"]?", line)
            if m:
                globs.append((m.group(1).strip(), "pnpm-workspace.yaml"))
    pkg = os.path.join(root, "package.json")
    if os.path.isfile(pkg):
        try:
            data = json.loads(read(pkg))
            ws = data.get("workspaces")
            if isinstance(ws, dict):
                ws = ws.get("packages", [])
            for g in ws or []:
                globs.append((g, "package.json"))
        except (json.JSONDecodeError, AttributeError):
            pass
    for g, where in globs:
        if g.startswith("!") or "*" in g:
            continue
        if not os.path.isfile(os.path.join(root, g, "package.json")):
            gaps.append({"kind": "workspace-member", "declared": g, "where": where})
    return gaps


def stub_files(root):
    """Source files that exist but hold no implementation."""
    out = []
    for path in walk(root):
        ext = os.path.splitext(path)[1]
        if ext not in TS_EXT | RUST_EXT:
            continue
        body = [
            ln.strip() for ln in read(path).splitlines()
            if ln.strip() and not ln.strip().startswith(("//", "/*", "*", "#"))
        ]
        if len(body) == 0:
            out.append({"file": rel(root, path), "non_comment_lines": 0})
    return out


def git_meta(root):
    def run(args):
        try:
            return subprocess.run(
                ["git", "-C", root] + args, capture_output=True, text=True, timeout=30
            ).stdout.strip()
        except (subprocess.SubprocessError, OSError):
            return ""
    return {
        "commits_available": run(["rev-list", "--count", "HEAD"]) or "?",
        "shallow": os.path.isfile(os.path.join(root, ".git", "shallow")),
    }


USAGE = "usage: abstraction_sweep.py <repo-or-source-tree> [--json]"
KNOWN_FLAGS = {"--json"}


def resolve_target():
    """Validate argv. Returns (path, exit_code); path is None when main should exit.

    A sweep that reports a denominator must not accept an argument it did not
    understand: printing "scanned=0" for a mistyped path or an unknown flag looks
    exactly like a clean result, which is the one output of a review that can do
    harm.
    """
    args = sys.argv[1:]
    if not args or any(a in ("-h", "--help") for a in args):
        print(__doc__)
        return None, 0 if args else 2
    unknown = [a for a in args if a.startswith("-") and a not in KNOWN_FLAGS]
    if unknown:
        sys.stderr.write("unknown option: %s\n%s\n" % (unknown[0], USAGE))
        return None, 2
    positional = [a for a in args if not a.startswith("-")]
    if len(positional) != 1:
        sys.stderr.write("expected exactly one path, got %d\n%s\n"
                         % (len(positional), USAGE))
        return None, 2
    root = os.path.abspath(positional[0])
    if not os.path.exists(root):
        sys.stderr.write("no such path: %s\n" % root)
        return None, 2
    if not os.path.isdir(root):
        sys.stderr.write("not a directory: %s\n" % root)
        return None, 2
    return root, 0


def main():
    root, code = resolve_target()
    if root is None:
        return code
    api = public_api_files(root)
    decls, impls = collect(root)

    unearned, unearned_public, zero_impl_rs, zero_impl_ts = [], [], [], []
    ext_traits = []
    for key, info in decls.items():
        lang, name = key
        all_sites = impls.get(key, set())
        prod = {s for s in all_sites if not TEST_HINT.search(s.split(":")[0])}
        tests = all_sites - prod
        # failures.md pays for an abstraction with "a second real implementation,
        # OR a concrete testing pain". Filtering test impls out therefore flags
        # the exact seam the criterion allows, so they count toward earning it.
        n = len(all_sites)
        rec = {
            "lang": lang, "name": name, "declared_at": f"{info['file']}:{info['line']}",
            "exported": info["exported"], "implementations": n,
            "prod_impls": len(prod), "test_impls": len(tests),
            "extension_trait_idiom": lang == "rs" and name.endswith("Ext"),
            "sites": sorted(all_sites)[:4],
        }
        if n == 0:
            # A TypeScript interface with no `implements` is almost always a
            # structural type — props, options, a response shape. Counting it
            # as an unbuilt promise floods the report with the normal case, so
            # it is tallied and excluded. A Rust trait is a contract, so zero
            # impls is worth surfacing — but only as low confidence, since
            # macro-generated impls are invisible to a regex.
            (zero_impl_rs if lang == "rs" else zero_impl_ts).append(rec)
        elif n == 1:
            if rec["extension_trait_idiom"]:
                # `impl FooExt for ForeignType` can only ever have one impl:
                # Rust's orphan rule makes that the point of the trait.
                ext_traits.append(rec)
            elif info["exported"] and info["file"] in api:
                unearned_public.append(rec)
            else:
                unearned.append(rec)

    gaps = workspace_gaps(root)
    stubs = stub_files(root)
    result = {
        "repo": root,
        "git": git_meta(root),
        "declarations_scanned": len(decls),
        "counts": {
            "unearned_internal": len(unearned),
            "unearned_public_api": len(unearned_public),
            "promised_never_built": len(gaps) + len(stubs),
            "workspace_gaps": len(gaps),
            "stub_files": len(stubs),
            "excluded_ts_type_shapes": len(zero_impl_ts),
            "zero_impl_traits_low_confidence": len(zero_impl_rs),
            "excluded_extension_traits": len(ext_traits),
        },
        "unearned_internal": sorted(unearned, key=lambda r: r["declared_at"])[:40],
        "unearned_public_api": sorted(unearned_public, key=lambda r: r["declared_at"])[:10],
        "workspace_gaps": gaps,
        "stub_files": stubs[:20],
        "zero_impl_traits_low_confidence": sorted(zero_impl_rs, key=lambda r: r["declared_at"])[:20],
        "excluded_extension_traits": ext_traits[:20],
    }

    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        c = result["counts"]
        print(f"{os.path.basename(root):10s} scanned={len(decls):5d} "
              f"unearned={c['unearned_internal']:4d} "
              f"public-api={c['unearned_public_api']:3d} "
              f"never-built={c['promised_never_built']:3d} "
              f"(ws-gaps={c['workspace_gaps']}, stubs={c['stub_files']})  "
              f"[excl: TS type-shapes={c['excluded_ts_type_shapes']}, "
              f"ext-traits={c['excluded_extension_traits']}, "
              f"0-impl traits={c['zero_impl_traits_low_confidence']}]")
        if not decls:
            print("  NOT APPLICABLE: zero boundaries scanned. This sweep looks for "
                  "declared boundaries (interface / trait / abstract class); a tree "
                  "without them — plain JavaScript or Python, for instance — yields "
                  "0 of 0, which means nothing was read, not that the code is clean. "
                  "Report it as inapplicable and go looking for multiplying "
                  "indirection and wrapper modules by reading instead.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
