# Templates

Placeholders are deliberate. Propose a default for each, and make rejecting it cost one word — the concrete form belongs to the user.

Omit any section with nothing real in it. A contract with three genuine invariants is worth more than one with a heading per category.

---

## 1. The contract — the only mandatory output

Ordered so the most-violated things come first, because attention decays down the page.

```markdown
# <Project>

<One line: what this is. Observed, confirmed by the user.>

## Stack & commands
<Observed. Dev, test, lint, typecheck, migrations.>

## Invariants
<From F4 and F7. What must hold — not why.
 Only things that break expensively AND silently.
 If a test or a type already catches it, it doesn't belong here.>

## Never
<From F3. Files not to open, each with a four-word reason.
 - Never open <file> — entire app in one file
 - Never read migrations in bulk — use the current schema instead>

## Shape of new code
<From Step 4b. Constrains what the model *writes*; everything above
 constrains what it must not break and what it must not read.
 Omit either slot the tree already answers consistently — an observed
 convention beats a written one, and costs nothing per session.

 Where it goes. One line per kind of thing:
 - A new module goes in <path>/<name>/ with <the files it must contain>
 - A new <endpoint / screen / migration> goes <where>, never <where>

 What it must satisfy. Only what no tool enforces. If a linter,
 formatter or type already catches it, it doesn't belong here —
 same rule as Invariants, same reason. Three real constraints beat
 a chapter; past the point where you're writing what a formatter
 would do, stop.>

**Remove when** a generator, template or lint rule enforces it. The cheaper
mechanism always wins.

## When → do → never
<From F5, F6, F8 and F2. This is the part that changes behaviour;
 everything above only changes knowledge. It's also the hook shortlist.>

| When | Do | Never |
|---|---|---|
| starting a session | read <state file> for the area you're touching | read the whole repo |
| adding an abstraction | name the second implementation first | build it "for later" |
| you see duplication | wait for the third occurrence | factor out on the second |
| a feature works end to end | check what it re-solved | build on top immediately |
| something looks non-idiomatic | check <decisions file> before changing it | assume it's a mistake |

## Where things are
<Routing table. One line per destination, so the model knows what to read
 and — more importantly — what not to.>
```

Past roughly 100 lines, something should have moved into `docs/`. Say so rather than letting it grow.

---

## 2. Partitioned state — only if F1 crossed its threshold

One file per area, plus an index.

```markdown
# <Area>

<What exists today and how it works. Present tense. Overwritten, never appended.>

## Open
<Real pending work only. Not a wish list.>
```

Put the rule that makes this work in the index itself: **these files describe the present and get overwritten; chronology lives in `git log`.** A doc that grows by accumulation stops being read and keeps costing.

---

## 3. Decision record — only if F2 was answered yes

```markdown
## <Number> — <Decision in one line>

<What was chosen.>

**Instead of:** <the idiomatic option that was rejected>
**Because:** <the reason, in a form that survives without you in the room>
**Trade-off:** <what this costs>
```

`Instead of` is the field that matters and the one almost nobody writes. Without it the record documents what exists; with it, the record defends the decision against being quietly reverted — which is the entire point of F2.

---

## 4. Invariant guardian — only if F4 was answered yes

Cheap model, read-only, one responsibility.

```markdown
---
name: <invariant-guard>
description: <when to invoke — before touching X, Y, Z>
tools: Read
model: <cheap>
---

Read the contract. Check the proposed change against the list below.
Report conflicts and nothing else. You do not write code.

Checklist:
- <invariant 1>
- <invariant 2>
```

Write the exit condition into the file itself: remove an invariant from the list as soon as a test or a type covers it. The cheaper mechanism always wins.

---

## 5. The ledger

Read when auditing or reviewing. Never during work — which is why provenance lives here and not in the contract, where it would cost context on every turn.

```markdown
# Scaffolding ledger

Read this when auditing or reviewing. Never during work.

## Installed

### <piece>
- **Prevents:** <failure ID and name>
- **Because you said:** "<their answer, verbatim>"
- **Remove when:** <exit condition — checkable from the repo>
- **Traces to:** <contract lines this produced>

## Not yet

### <piece>
- **Skipped because:** <the gating answer>
- **Revisit when:** <revisit condition>

## Run count
- Installed: <n>
- Skipped or removed: <n>
```

The count isn't decoration. If installations outnumber exclusions and removals, the run drifted toward ceremony and that's worth saying out loud.
