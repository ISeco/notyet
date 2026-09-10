# The nine failures

Each entry: what the model does, the question only the user can answer, the threshold worth suggesting, and the condition for taking it back out.

**Configuration failures** (F1, F3, F4, F7, F9) produce files. **Work failures** (F5, F6, F8) produce triggers. **F2** does both.

Two framing points that carry the whole set:

- Every piece counters a *named failure of the model*, not a shortcoming of the developer. If you can't name the failure, don't add the piece.
- The risk inverts compared to solo work. A developer alone under-engineers out of haste; the model over-engineers by default, because its corpus rewards the appearance of rigour. The criterion has to push the opposite way from usual.

**On the questions.** The failures are the model's and apply to anyone who types. The questions are about the project, and most can be asked without any programming vocabulary. Where a question has two forms below, use the **plain** one for anyone who can't read the code themselves (third gating question) — and, honestly, it's usually the better question for developers too.

---

## F1 — No memory between sessions

> The model retains nothing between sessions. Any context that isn't written down is rebuilt from scratch — or guessed at — every single time.

**Question.** What would you have to explain again if you came back to this after a week away?

This is the root failure; five artefacts derive from it, each answering a different *kind* of missing memory: the contract (what is inviolable), the decision record (why you chose the non-obvious thing), partitioned state (where the project stands today), the map (what touches what), and the close protocol (how all of the above survives the session).

**Threshold.** Write down the memory you have already reconstructed twice. Not before — that's speculation. Not later — you've already paid for it twice.

**Exit conditions**, all checkable from the repository:

| Piece | Retire when | How to check |
|---|---|---|
| Contract | it mentions files, paths or patterns that no longer exist | grep each mention against the file tree |
| Decision record | the code no longer does what the decision claims | read the decision against the code it describes |
| Partitioned state | the area it describes is gone, or its content contradicts the code | compare the index against the real structure |
| Map | its date precedes the last commit touching what it maps | map timestamp vs. `git log` |
| Close protocol | the project is finished | — |

**A rule that makes partitioned state work:** state files describe the present and get overwritten. Chronology lives in `git log`. A doc that grows by accumulation stops being read and keeps costing.

---

## F2 — Reversion to the idiomatic

> The model reverts deliberate non-idiomatic decisions back toward the default. It does not ask first.

**Question.** Have you chosen anything against the obvious option, where the reason isn't visible in the code itself?

*No plain form.* Someone who can't read the code hasn't chosen against any default — they've accepted every one the model offered. Skip this failure for them; their exposure is the mirror image and lives under F5.

**Threshold.** Record a decision when it was deliberate against the idiomatic choice, or would be expensive to reverse — and isn't evident from reading the code.

**Exit condition.** Remove it when the decision is no longer reversible. But if the *code* stopped honouring it, don't delete the record — fix one or the other. A record left lying is exactly the stale piece the model keeps obeying.

The field that does the work here is **`Instead of:`** — the idiomatic option that was rejected. Almost nobody writes it, and without it the record documents what exists rather than defending it.

*Status: this failure is a hypothesis. The artefact that motivates it is real; that the model actually reverts is the most plausible explanation, not a measured finding. Present it as such.*

---

## F3 — Undiscriminating context consumption

> Everything the model reads to orient itself stays in the context window for the rest of the session — relevant or not. Left alone, it will open the largest files in the repository.

**Question.** Which files here are large, generated or exported — and would look relevant to someone exploring?

**Two answers, different mechanisms.** A prohibition list (cheap, high return, and the best candidate for a deterministic hook — a written "never open X" is precisely what gets skipped under context pressure). And a cheap exploration subagent, whose real benefit is context isolation rather than saving money: it reads five files and returns a summary; without it those five files stay in the main window all session. People adopt it for cost and abandon it because the saving is marginal — the reason is the other one.

**Exit conditions.** The prohibition goes when the file is deleted or partitioned into usable pieces. The exploration subagent has none, and it's the clean example of why: it lives in its own file, isn't read unless invoked, and asserts nothing about the project. It costs nothing sitting idle.

Universal candidates for prohibition: lockfiles, accumulated migrations, snapshots, build output, design exports, generated reports.

---

## F4 — Silent invariant breakage

> The model breaks invariants that fail silently while refactoring something unrelated. The diff looks reasonable.

**Question.** What can break here without a single test failing, a type erroring or a log firing?
**Plain form.** What would be a disaster if it went wrong and nobody noticed? — *"two people booking the same slot"*, *"a payment recorded twice"*, *"one customer seeing another's data"*. They can name it even if they can't name the mechanism.

**Threshold.** An invariant that is **expensive AND silent** when broken. Both, not either.

**Exit condition, and the most useful rule in the set:** if a linter, a test or the type system already catches it, you don't need scaffolding. Retire the guardian for an invariant the moment the cheaper mechanism covers it.

Indentation needs no guardian. A missing user-scope filter on a query does: it breaks tenant isolation, throws nothing, and the diff looks fine.

---

## F5 — Over-engineering by pattern-matching

> The model produces the maximal idiomatic version, not the minimum that works. Its corpus rewards the appearance of rigour: interfaces, layers, named patterns.

**Question.** Is there a second implementation today — or one you're nearly certain is coming?
**Plain form.** Does this need to work two different ways, or one? — *"do you accept one payment provider or several?"*, *"one kind of user or two?"*. If the answer is one, whatever the model built to handle several is weight.

This single failure covers six things that are usually treated as separate criteria: layered architecture, single responsibility, strategy hierarchies, dependency inversion, repository interfaces, value objects. As published advice they add nothing new. As symptoms of one bias they're useful — and framing them this way keeps the skill out of a thirty-year-old argument it has no need to enter. **Don't teach patterns.** Assume the model will propose them anyway; contribute the thing it won't — when to say no.

**Threshold.** An abstraction is paid for by a second real implementation, or by a concrete testing pain. Never "just in case".

**Exit condition.** A great deal is written about when to introduce an abstraction and almost nothing about when to withdraw one. Every abstraction enters with a review date: *if the second implementation hasn't arrived and it isn't easing any test, collapse it.*

That suggests a review-mode sweep in **both directions**:

- **Unearned:** a declared boundary with exactly one implementation. Justified by a future that didn't arrive.
- **Promised and never built:** a boundary declared in build configuration with nothing behind it — a workspace member listed but absent, a module referenced but empty. The cost is paid somewhere else, usually as hand-duplicated code.

**Treat the output as candidates, not findings.** This was measured across four codebases — three mature public repositories in TypeScript and Rust, plus an app generated from a feature-only prompt — and the result does not support calling it a check. Of 29 candidates, **72% were false positives on inspection and none were confirmed unearned.** Every candidate needs a human verdict before it reaches a remove list.

**Always report the denominator: boundaries scanned, then candidates found.** An empty result has two incompatible causes and the count is the only thing that separates them. `0 of 1324` means the code carries no abstraction debt. `0 of 0` means the sweep had nothing to look at — the normal case in an untyped language, which is what the model writes for someone who asked it to "use whatever is normal". Reporting a bare empty to that person says they have no abstraction debt when the truth is that nobody looked.

**So the sweep applies to languages that declare boundaries** — interfaces, traits, abstract classes. In plain JavaScript or Python the failure still happens, but the symptom is different: indirection and wrapper modules multiplying, rather than interfaces with one implementation. Say the sweep doesn't apply instead of issuing a clean bill of health, and go looking for the proliferation by reading.

**What does not count as unearned.** Each row is a real false positive from the measurement:

| Not unearned | Why |
|---|---|
| A published contract | Exported from the package's public API — consumers are the second implementation. Needs re-export chains followed, `export type { X } from` included |
| Implemented only in a test | The threshold above pays for an abstraction with a testing pain, so filtering test implementations out flags the exact seam the criterion allows |
| A generated file | A 16k-line `.d.ts` from a codegen tool is not a design decision |
| An extension trait | `impl FooExt for ForeignType` can only ever have one implementation; Rust's orphan rule makes that the point of it |
| `interface A extends B` | Type composition, not implementation. Counting it flags every wire-format union member |
| Example or experimental code | Not the project's own abstractions |
| Same name, different package | In a monorepo, name-keyed matching collides two unrelated types |
| A structural type | A TypeScript `interface` is usually a data shape — props, options, a response body. Zero implementations is its normal state, not a broken promise |

`scripts/abstraction_sweep.py` implements all of these and prints the denominator. Expect the rate to track language idiom rather than code quality: the same script returned candidates for 0.15% of boundaries in one mature repository and 8.8% in another, so the number is not comparable across stacks and is not a quality measure.

---

## F6 — Premature DRY

> The model deduplicates on second sight, factoring out two similar blocks before the real abstraction has revealed itself.

**Question.** Is this the third occurrence, or the second?

**Threshold.** Rule of three. Premature DRY creates worse coupling than the duplication it removed.

**Exit condition.** Inline the helper back if the third case never arrived, or if callers keep passing flags to bend it into shape.

---

## F7 — Silent correctness gaps

> The model writes multi-step operations as sequential writes, and working code with holes that never surface in the diff. Nothing errors. The feature works.

**Question.** Does this operation span more than one write that must all succeed or all fail? And does the project handle authentication, someone else's data, or a public repository?
**Plain form.** Is there anything that has to happen all-or-nothing — *charging the card and recording the order, moving money out of one place and into another*? And do people log in, or does it hold anyone's data but yours?

**No cost-benefit argument.** This is the one family with no negotiable threshold: atomicity and security are correctness, not architecture. No exit condition — exposure only grows.

*Status: the security threshold here is industry common sense rather than distilled experience. Keep it because its absence would be noticed; don't present it as a contribution.*

---

## F8 — Plausible divergence

> The model produces local solutions that are plausible and quietly diverge from what the codebase already does — and produces them fast. Drift accumulates faster than with human contributors because the volume per session is higher.

**Question.** After a feature works, do you check whether it solved a problem your codebase had already solved somewhere else?

**Threshold.** Once a feature works end to end, before building on top of it. Not on every fix.

**The rule that stops it becoming an endless refactor:** fix only what has a **confirmed second occurrence**. This is deduplication against something that already exists, not speculative abstraction. If there's nothing to converge on, that's a decision to record, not a silent refactor.

Concrete symptoms worth looking for: hand-rolled UI duplicating a shared primitive, domain formatting reimplemented locally, a hardcoded literal where a shared token exists, the same domain fact encoded in two places.

**Exit condition.** It's a ritual rather than an installed artefact, so it retires per feature: stop passing over one whose files have gone quiet.

This is the gap no tool covers, and it sits between the two layers — its trigger is a session ritual, its payload is engineering.

---

## F9 — Audience blindness

> The model applies the same ceremony regardless of who reads the result — full commit conventions on a throwaway script, database entities leaking straight out of a public API.

**Question.** Who reads this code, and how long will the project live?

**Threshold.** Invest in proportion to the reader. For a portfolio repository whose whole point is visible code, the history is part of the product. For a private disposable script it's theatre. On a public or external surface, separating the wire format from the storage format stops being taste and becomes correctness.

**Exit condition.** The only one that must be asked rather than observed, because neither variable is visible in the repository: did the audience change, or the expected lifespan? A repo that stopped being public no longer justifies the ceremony that the reader justified.

These are the two variables the model cannot infer — which is why they're also the two gating questions that open the interview.

---

# Candidate failures

Observed once, not yet confirmed. Treat as hypotheses: mention them where they apply, don't build scaffolding on them alone.

## F10 — The plan documented as the state

> Ask the model for a design and it produces complete, confident documentation of things that do not exist yet. From that moment on, everyone — including the model in later sessions — reads it as descriptive.

**Question.** Was this document written before the code it describes, or after?

**Threshold.** Any document produced during planning carries a marker separating intent from state, or gets a reconciliation pass when the thing is actually built.

**Exit condition.** The marker comes off once the document has been checked against the code at least once — observable from git: the doc has a commit that postdates the code it describes.

**Why it's the model's failure and not the developer's.** The model produces complete, confident documentation on request without distinguishing what exists from what is planned. It won't say "this isn't built yet" unless asked. And the founding asymmetry applies with full force: in later sessions it obeys that documentation.

**How it differs from drift (F1).** Drift is a document that was true and aged. This is a document that was never true — it described an intention. The fix is different: drift wants an update rule; this wants a reconciliation step, once, when the plan becomes real.

**The one observation.** A production codebase whose contract and four reference docs were all created in the first commit, describing the app as intended. Six weeks later every false claim traced back to that commit, or to a correction appended beside the old line rather than replacing it. The state files that were written *after* each feature shipped stayed accurate; the plan-era docs never caught up.

**Mechanical check, usable in review mode today:** for each doc, compare its first commit against the first commit of the code it describes. A doc older than its subject was written as a plan.
