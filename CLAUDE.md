# CLAUDE.md — notyet

The only piece of scaffolding this repository has earned so far.

It exists because the update rule was missing, and that cost two real mistakes in a single day: `references/measurement.md` shipped without `SKILL.md` naming it, and `README.md` claimed the file was included while it was not. Sweep 4 of this project's own review mode exists to find that gap, and found it here. By F1's threshold — write down the memory you have already reconstructed twice — the rule is earned; before those two mistakes it was correctly a "not yet".

Nothing else is in this file. When a second thing gets reconstructed twice, it earns a section. Do not add invariants, prohibitions or a file map here on the grounds that contracts usually have them.

## The update rule

After changing anything under `skills/notyet/`, work down this table:

| If you changed | Update |
|---|---|
| a file in `references/` — added, removed or renamed | the References section of `SKILL.md`, **and** the "What's in the box" table in `README.md` |
| the name of `references/setup.md` or `references/review.md` | also the routing paragraph in `SKILL.md`'s "Two modes" section, which names both files in the body and not just in the References list — this row exists because splitting the modes revealed the row above was not enough |
| what a script reports, refuses or covers | that script's line in `SKILL.md`'s References section, its row in the README table, **and** the sweep's own paragraph in `references/review.md` |
| a sweep's status, or the evidence behind it | its status line in `references/review.md` **and** the matching bullet in `README.md`'s "Where the evidence stops" |
| the `description` in `SKILL.md`'s frontmatter | nothing else — but re-measure it before trusting the change, because a description that reads well and matches nothing people actually type has a recall problem that is invisible from the inside |
| anything a user of the skill would notice | `version` in `.claude-plugin/plugin.json` **and** in `.claude-plugin/marketplace.json` — they are two files with the same number in them |

**Where drift lands here:** four places have to agree with the files, and nothing automatic checks any of them — `SKILL.md`'s References section, its routing paragraph, the README's "What's in the box" table, and the README's "Where the evidence stops" list. Every mistake this repository has made so far was one of them disagreeing with reality.

**A worked example of why this file exists.** Splitting the two modes out of `SKILL.md` made two rows of this very table stale within minutes of writing them: they pointed at sweep paragraphs that had just moved to `references/review.md`. Caught by re-reading the rule while applying it, not by any mechanism. That is the asymmetry this skill is built on, aimed at itself — a stale rule is worse than a missing one, because the next reader obeys it.

## What this file is not

It is not shipped to anyone who installs the skill. Claude Code reads `CLAUDE.md` from the project you are working in, not from an installed plugin's directory, so this file costs context to people working *on* notyet and nothing to people working *with* it. If that ever stops being true, this file has to move out of the plugin root.

## Exit condition

Retire it if `skills/notyet/` ever collapses to a single file with no references and no scripts, because then there is nothing left to keep in sync.
