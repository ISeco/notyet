# Mode: Setup

You are here because `SKILL.md`'s routing rule sent you: no ledger exists in the
repository, so this project has no scaffolding anyone decided on. Everything in
`SKILL.md` still applies — the premise, the assert/ask line, and the success
criterion that a good run produces more exclusions and removals than
installations.

## Step 1 — Observe before you ask

Asking for something you could have read is worse than useless: it costs the person time and their from-memory answer is less accurate than counting. Read the repo first and fill in everything on the left.

| Observe | Ask |
|---|---|
| Stack, size, surfaces, monorepo or not | How long the project needs to keep working |
| Large, generated or exported files | Who else reads it or depends on it |
| Scaffolding that already exists | What must never break |
| Test and type coverage | What was chosen deliberately against the obvious option |
| Auth present, repo public or private | What hurts today |
| Length of git history | |

Close this step by telling them what you found and inviting correction. Reading a repo wrong and then building on it is expensive.

## Step 2 — The three gating questions

> **How many more weeks does this project need to keep working?**
> **Who else reads this code or depends on it — now or later?**
> **Can you read the code yourself, or do you rely on the model to tell you what it does?**

The first two are worth more than the rest combined, because almost all scaffolding is amortised over time or justified to somebody. They're also precisely the two variables the model can never infer on its own.

- **Short life / disposable** → almost everything switches off. Only silent-correctness survives, and only if the project touches authentication or someone else's data. *"Your project needs none of this except two security checks"* is a successful outcome, not a failure.
- **No audience, private** → repository hygiene stops being product and becomes theatre. Scale it down.

The third changes how conservative you are, not which failures apply. The failures are the model's; they happen to everyone who types. What changes is whether there's anyone downstream to catch the model over-building — and if the person can't read the code, there isn't.

- **Can't read the code** → install *less*, not more. Everything you install is something they can't audit and can't remove later, so the threshold for every piece goes up and the "not yet" list gets longer. Explain each installed line in plain terms in your response, because the file itself won't be read. Use the plain-language form of every question in `references/failures.md`, and skip F2 entirely — they haven't chosen against any default; they've accepted all of them, which is its own exposure and is covered by F5.

Someone who can't read code is the user for whom "install less" matters most. This is the same subtractive criterion, applied where it has the fewest safety nets.

*This third question is design reasoning, not yet tested with anyone who fits it. Treat the guidance as a starting position.*

Everything a gating answer switched off goes straight into the "not yet" list with the reason. That list costs you nothing to produce — it's a by-product of gating — and it's the most useful thing you'll hand over.

## Step 3 — Walk the failures that survived

Read `references/failures.md` for the full set. Configuration failures produce files; work failures produce triggers.

Order matters — go in dependency order, because F1 underlies most of the rest:

1. **F1 — no memory between sessions.** The root failure. Five artefacts derive from it.
2. **F3 — undiscriminating context consumption.** Mostly observed. Propose the prohibition list you already detected and ask for confirmation, rather than asking in the abstract.
3. **F4 — silent invariant breakage.** Irreducibly a question. If nothing breaks expensively *and* silently, there's no guardian.
4. **F7 — silent correctness gaps.** Half observed, half asked.
5. **F2 — reversion to the idiomatic.** Ask last in this phase — by then they're thinking about their project in these terms and can actually answer it.

For each: name the failure, ask its question, and only if the answer warrants it, propose the threshold with its cost and its exit condition.

## Step 4 — Work failures, as a block

F5, F6 and F8 describe the model, not the project, so asking *"does this apply to you?"* is the wrong question — it applies to everyone. Propose them as a block of triggers for the contract and let them strike any they don't want.

Each of these lines is also a candidate for a deterministic hook, because written instructions get skipped under context pressure while a hook does not. A hook can **fire or block**; it cannot **judge**. So the trigger table is the hook shortlist, and everything requiring judgment stays as instruction. Tool-specific hook syntax lives in `references/tooling.md`, never in the contract itself.

## Step 5 — Write the output

Templates are in `references/templates.md`.

**The minimum output is one file: the contract.** Everything else has to be earned by an answer. Omit empty sections rather than writing "N/A" — a contract with three real invariants beats one with a heading for every category.

Then hand over:

1. The files.
2. **The "not yet" list**, with the reason and the revisit condition for each item.
3. **The ledger**, which records what was installed, why, its exit condition — and everything skipped with its revisit condition. But apply your own criterion to it: on a project that will be deleted in weeks, a ledger is a file nobody will ever reopen, so put the same content in the response and skip the file. A ledger earns its place when there will be a review to read it.
4. **The count**: installations vs. exclusions plus removals.
5. **The measurement file** — `references/measurement.md` — but only if the project will still be here in a month. Six development sessions, three before and three after a single adjustment pass, measuring auto-compaction, files read before the first edit, and anything re-explained that was already written down. It is the only way anyone finds out whether the pieces you just installed do anything, and it deletes itself once its conclusion is written. On a short-lived project, skip it and say why.
