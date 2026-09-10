# notyet

A Claude Code skill that sets up — or prunes — the scaffolding that makes a codebase workable for an AI coding agent.

Its most useful output is usually the list of what your project does **not** need yet. Hence the name.

## Install

```
/plugin marketplace add ISeco/notyet
/plugin install notyet@notyet
```

It has also been submitted to the community marketplace. Once it's listed there, `/plugin marketplace add anthropics/claude-plugins-community` followed by `/plugin install notyet@claude-community` will work too.

## Why this exists

Most advice about `CLAUDE.md`, `AGENTS.md` and `.cursorrules` tells you what to add. Almost none tells you what to leave out, or when to take something back out.

That asymmetry matters more than it sounds, because scaffolding is not free. Every piece costs context on every session, costs maintenance, and can drift out of sync with the code. And there is a failure mode here that does not exist between human collaborators:

> **A stale piece of scaffolding is worse than a missing one.** A human sees an outdated doc and distrusts it. The model obeys it.

So a piece has to buy a concrete benefit today that beats that cost. `notyet` is the criterion for deciding that, question by question.

## What it does

**Setup mode** — for a project with no scaffolding, or ad-hoc scaffolding nobody decided on. It reads the repo first, asks three gating questions, walks the model failures that survived those answers, and writes the minimum: one contract file. Everything else has to be earned by an answer.

**Review mode** — for a project that was set up before, coming back to see what is now dead weight. Six sweeps, then three lists: **remove**, **add**, and **drift** — the dangerous one, because a contract promising an invariant the code stopped honouring is actively harmful.

Review mode reads only. It never installs or runs anything, which is what makes it safe to point at a repository you did not write.

### The success criterion

**A good run produces more exclusions and removals than installations.**

A skill meant to prevent over-engineering that installs six files on first contact has refuted itself. The run reports both counts at the end, so you can hold it to this.

### What it asserts, and what it asks

- **How the model fails** is shared, observable, and asserted. Anyone can verify it. It does not depend on whose project this is.
- **What your project needs** depends on your project. It asks. It never decides that for you.

Four layers of decreasing imposition: failure (asserted) → question (you answer) → threshold (suggested, always with its cost and its exit condition) → concrete form (yours; the default costs one word to reject).

### The three gating questions

> How many more weeks does this project need to keep working?
> Who else reads this code or depends on it — now or later?
> Can you read the code yourself, or do you rely on the model to tell you what it does?

The first two are worth more than the rest combined, because almost all scaffolding is amortised over time or justified to somebody — and they are precisely the two variables the model can never infer on its own.

*"Your project needs none of this except two security checks"* is a successful outcome, not a failure.

## For people who don't write code

It works. The nine failures are the model's; they happen to everyone who types, whether or not you can read the output.

What changes is the conservatism, and it changes in the direction people don't expect: if you can't read the code, the skill installs **less**, not more. Everything it installs is something you can't audit and won't remove later, so the threshold for every piece goes up and the "not yet" list gets longer. Every installed line gets explained in plain terms in the response, because the file itself won't be read.

You are the user for whom "install less" matters most, and that guidance is the part of this skill with the least evidence behind it — see below.

## What's in the box

| Piece | What it is |
|---|---|
| `SKILL.md` | Both modes, the gating questions, the six sweeps, the output rules |
| `references/failures.md` | The nine model failures — each with its question, threshold and exit condition, plus candidates observed once and not yet confirmed |
| `references/templates.md` | The exact shape of every file it might write |
| `references/tooling.md` | Capability → tool mapping, including hooks. Kept separate so the criterion doesn't expire when tools change |
| `scripts/abstraction_sweep.py` | Review sweep 2, with the exclusion table applied and the denominator printed |
| `scripts/staleness_sweep.py` | Review sweep 3, last-commit and first-commit comparisons. Refuses a shallow clone, where the dates lie without erroring |

Both scripts read only. Neither installs or executes anything in the repository you point them at.

## Where the evidence stops

This is criterion distilled from building one application with an agent, plus measurement against four other codebases. It is not a measured result, and the honest boundaries are worth stating up front:

- **Most of the criterion is n=1.** One project, one stack, one developer. Where a threshold has no independent support, `failures.md` says so.
- **The abstraction sweep produces candidates, not findings.** Measured across four codebases: 72% of what it returned were false positives, and none were confirmed unearned. It discriminates language and repo composition more than code quality — the rate varied sixtyfold between two equally mature repositories. It ships with an exclusion table built from those real false positives, and it always reports the denominator, because `0 of 1324` means the code is clean while `0 of 0` means the sweep had nothing to read.
- **Two failures are candidates, not confirmed.** F2 and F10 are marked as hypotheses in `failures.md`, with the condition each needs to be promoted.
- **The guidance for non-programmers is design reasoning, untested.** Nobody who fits that description has run it yet. Treat it as a starting position.
- **Setup mode has never run on a large repository.** Review mode has, against a Rust codebase with twenty thousand commits. But the setup flow was designed for a project that is starting or halfway through, and what its first phase costs on a large established repo is unmeasured.
- **Sweep 2 is the weak member of the six.** Measured twice without earning its place, and marked as such in `SKILL.md` rather than quietly presented alongside the others.

If you run it and it gets something wrong, that is the useful outcome — open an issue. The measurement template is included precisely because one person cannot generate the n>1 this needs.

## What it is not for

Writing hook syntax, CI pipelines, agent harness code, or skills. Explaining which tool reads which file. It also does not touch the model's harness — on the word "scaffolding", see the first section of `SKILL.md`.

## License

MIT — see `LICENSE`.

**The files this skill writes are yours.** The license covers `notyet` itself: the skill, its references, and its scripts. A contract, ledger or "not yet" list produced by a run in your repository is your work product. It carries no obligation from this project and needs no attribution — including anything built from the templates in `references/templates.md`.
