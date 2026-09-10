---
name: notyet
description: 'Use this skill whenever someone asks what rules, instructions or repo structure an AI coding agent (Claude Code, Cursor, Windsurf, Copilot) needs to work well in THEIR project — or whether it needs any at all. Triggers: what to put in CLAUDE.md, AGENTS.md or .cursorrules; preparing a repo or team for AI-assisted development; the model keeps forgetting things, re-reading huge files, ignoring a rule, or over-building; an instruction file that grew too long or went stale; merging conflicting personal rule files into one shared contract; "do I really need a CLAUDE.md for this small or throwaway project?" (the answer may be no). Works for non-programmers building with an agent, in any language. It reads the repo, writes the minimal contract (invariants, prohibitions, triggers) plus an explicit not-yet list, and in review mode finds drifted docs and unearned abstractions. Not for writing hook syntax, CI pipelines, agent harness code, skills, or generic explanations of which tool reads which file.'
---

# notyet

Set up — or prune — the scaffolding that makes a codebase workable for an AI coding agent. Its most useful output is usually the list of what the project does *not* need yet.

**A note on the word "scaffolding".** In agent-architecture writing it means the code around the model — the control loop, tools, state. Here it means the other thing: the files and rules around the *project* that tell an agent how to behave in it. Contract, docs, prohibitions, subagents. Nothing in this skill touches the model's harness.

## The premise

Every piece of scaffolding costs something: context on every session, maintenance, and the risk of drifting out of sync with the code. So a piece has to buy a concrete benefit today that beats that cost.

There is an asymmetry here that does not exist between human collaborators, and it drives most of what follows: **a stale piece of scaffolding is worse than a missing one.** A human sees an outdated doc and distrusts it. The model obeys it.

## What you assert, and what you ask

This is the line that keeps the skill useful without making it bossy:

- **How the model fails is shared, observable, and yours to assert.** Anyone can verify it. It doesn't depend on whose project this is.
- **What this project needs depends on this project.** Ask. Never decide it for them.

Concretely, four layers of decreasing imposition: **failure** (assert) → **question** (they answer) → **threshold** (suggest, always with its cost and its exit condition) → **concrete form** (theirs; propose a default that costs one word to reject).

Before writing any line, ask yourself: *would this claim be false if the project were different?* If yes, it's a prescription — turn it into a question. If no, it's about the model and you can state it.

## The success criterion

**A good run produces more exclusions and removals than installations.**

This matters more than it sounds. A skill meant to prevent over-engineering that installs six files on first contact has refuted itself. The most valuable thing you produce is usually the list of things the project does *not* need — that's the part that removes work rather than adding it.

Count both and report the count at the end. If installations outnumber exclusions plus removals, say so plainly and reconsider what you proposed.

## Two modes

**Setup** — a project that has no scaffolding, or ad-hoc scaffolding nobody decided on.
**Review** — a project that was set up before, coming back to see what's now dead weight.

If a ledger (`docs/scaffolding-ledger.md` or equivalent) already exists, this is a review. Otherwise it's a setup.

**Then read exactly one of them:** `references/setup.md` or `references/review.md`. They are separate files because a run is in one mode and never both, and the mode you are not in would otherwise cost context on every single activation — which is the dead weight sweep 5 exists to find. Do not read both to decide; the rule above decides.

---

# Output rules

**Traceability lives outside the contract.** Every line you write must trace to an answer or to a named failure — but annotating that inside the contract makes it cost context on every turn of every session, which is the exact error the contract exists to prevent. Provenance goes in the ledger, read only when auditing.

**Nothing enters because it worked somewhere else.** If you can't point to their answer or to a named model failure, it doesn't go in.

**Watch the contract's size.** Past roughly 100 lines, something should have moved into `docs/`. Say so.

**Exit conditions must be checkable.** One nobody can evaluate is the same as none — and a recommendation without an exit condition is a mandate in disguise. "If you haven't read it in a few sessions" fails this: nobody remembers and nothing records it. Only pieces that cost per session, or that can fall out of sync, need one at all; a subagent nobody invokes costs nothing sitting idle.

---

# References

- `references/setup.md` — the setup procedure: observe, the three gating questions, the failures that survived them, and what to write. Read when the routing rule says setup.
- `references/review.md` — the review procedure: the six sweeps and the three output lists. Read when the routing rule says review.
- `references/failures.md` — the nine model failures, each with its question, threshold and exit condition, plus candidates observed once and not yet confirmed. Read at the start of either mode.
- `references/templates.md` — exact shape of every file you might write. Read before Step 5.
- `references/measurement.md` — the before/after template an adopter fills in to find out whether the scaffolding helped in their project. Read at Step 5, and only for a project that will outlive the measurement.
- `references/tooling.md` — capability → tool mapping, including hooks. Read only when you need the concrete syntax for a specific tool. Kept separate so the criterion doesn't expire when tools change.
- `scripts/abstraction_sweep.py` — runs review sweep 2 over a repository and prints candidates with the denominator. Reads only; never installs or executes anything in the target. Run it rather than grepping by hand, then adjudicate what it returns.
- `scripts/staleness_sweep.py` — runs review sweep 3: last-commit and first-commit comparisons between each doc and the code it references. It reads every markdown file outside vendored and build directories, and labels each zero with the reason it is zero: docs skipped as vendored, docs that name no source file, pairs last changed on the same day that day-granular dates cannot order, and a codebase whose languages it cannot follow. Refuses a shallow clone, where the dates lie without erroring. Reads only. A `--filter=blob:none` clone is enough and is fast even on a repository with twenty thousand commits.
