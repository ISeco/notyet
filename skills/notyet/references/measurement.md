# Measuring whether the scaffolding actually helped

Everything in this skill is criterion, not measurement. It comes from one project, one stack, one developer — and no amount of careful reasoning fixes that. This file is how you find out whether the pieces you installed do anything in *your* project, and it is the only route to the n>1 that the criterion needs.

Offer it after a setup run, and only when the project will still be here in a month. On a repo that gets deleted in three weeks, six measured sessions never happen: skip it and say so.

**This file is temporary.** It describes an experiment, not the project, so it does not belong in permanent documentation. Its exit condition: both blocks filled in and the conclusion written. Then delete it. A measurement file that survives its own conclusion is exactly the stale scaffolding this skill exists to remove.

## Three definitions, so the numbers are comparable

**1. Auto-compaction.** Did the session compact context on its own? `yes` / `no`. If yes, note roughly when ("halfway through the implementation").

**2. Files read before the first edit.** How many distinct files were opened — read, catted, grepped with content — between the start of the session and the first write to code. Count the contract and the docs. This measures what it costs to *get oriented* before producing anything.

**3. Did you re-explain something already written down?** `yes` / `no`, **and what**. This is the most valuable column by a wide margin. Every `yes` is a bug in the scaffolding, not in you, and it has exactly two diagnoses: the fact was there and wasn't found (a routing problem), or it wasn't there (a coverage problem). The fix differs.

## Block A — baseline

Three real development sessions with the scaffolding exactly as it is. Change nothing while measuring; optimising mid-measurement destroys the comparison.

| # | Date | What you worked on | Auto-compaction | Files before first edit | Re-explanation? (what) |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

**Block A notes:**

## Adjustment

One row per `yes` in Block A's last column. Nothing else — a measurement that becomes an excuse to redesign everything has stopped being a measurement.

| Re-explanation observed | Diagnosis (missing, or present but not found?) | Fix applied |
|---|---|---|
| | | |

## Block B — after the adjustment

Three more sessions, same definitions.

| # | Date | What you worked on | Auto-compaction | Files before first edit | Re-explanation? (what) |
|---|---|---|---|---|---|
| 4 | | | | | |
| 5 | | | | | |
| 6 | | | | | |

**Block B notes:**

## Conclusion

Compare A against B and write **one sentence containing a number**. The shape to aim for:

> "From 3 compactions in 3 sessions to 0, and from an average of 9 files before the first edit to 4."

If there is no difference, that is also a result and it gets reported the same way. **An honest number that contradicts the hypothesis is worth more than no number at all** — and for this skill it is worth more than a confirming one, because a confirming result from the author is what it already has.

## Known biases — write these down before concluding anything

- **Sessions are not equivalent.** A new feature costs more than a fix. Recording what you worked on is what lets you throw out an unfair comparison.
- **The project grows between blocks**, which pushes the numbers up on its own.
- **The person measuring designed the scaffolding.** Record each figure during the session, not reconstructed from memory at the end.
- **Six sessions is a small sample**, and this is a before/after with no control. It tells you whether something plausibly changed in your project. It does not establish a general result.

## Reporting it

If you fill this in, the numbers are useful beyond your own repo — including the ones that contradict the criterion. Open an issue on the repository with the conclusion sentence, your stack, and roughly the size of the project. Nothing else; no code, no contract contents.

That is the whole mechanism by which this stops being one developer's judgement.
