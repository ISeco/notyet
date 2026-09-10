# Capability → tool mapping

**Read this only when you need concrete syntax.** It's kept separate on purpose: tools get renamed, change APIs and get abandoned, and the criterion shouldn't expire when they do. Everything else in this skill reasons in capabilities — "you need a persistent map", "you need this prohibition enforced" — and resolves to specific tools only here.

If a tool named below no longer exists or behaves differently, replace this file. Nothing else needs to change.

---

## Capabilities the criterion asks for

| Capability | What it must do | Where it usually lives |
|---|---|---|
| Behaviour contract | Loaded automatically at session start, every session | `CLAUDE.md`, `AGENTS.md`, `.cursorrules` — one file at repo root, by convention of the tool. Needing two names is common; **symlink the second to the first** rather than keeping two copies. That is the difference between one source of truth and a drift generator maintained by hand, and a repository observed doing both at once had its symlinked contract in sync and its eight hand-copied guides all diverged |
| Read prohibition | **Block** a file from being read, not merely discourage it | A pre-tool hook that denies matching paths |
| Session open / close | Fire on start and end without being asked | Session lifecycle hooks |
| Invariant check | Fire on edits to given paths; a cheap model judges | Subagent + a pre- or post-edit hook that triggers it |
| Cheap exploration | Read many files, return a summary, keep them out of the main window | Subagent with read-only tools on a small model |
| Persistent map | Survive between sessions, regenerate on demand | Generated index, or a hand-written module map |
| Transport compression | Shrink what does pass through — tool output, logs, file contents, history | A proxy or MCP layer between the agent and the model |

---

## What can be a hook, and what can't

The distinction that matters: **a hook can fire or block; it cannot judge.**

Written instructions are probabilistic — under context pressure they get skipped, even from the contract. Hooks are deterministic. So anything expressible as a condition should become one, and anything requiring criterion should stay as instruction.

| Failure | Mechanism |
|---|---|
| F3 — prohibitions | **Hook, and the best case.** Blocking a read is purely deterministic, and "never open X" is the instruction with the widest gap between what it promises and what it delivers |
| F1 — session open/close | **Hook.** Opening by reading the area's state and closing by writing it is mechanical |
| F4 — guardian | **Hook for the trigger**, instruction for the verdict |
| F8 — standardization pass | **Hook for the trigger** (tests just passed), instruction for the analysis |
| F2, F5, F6 | **Instruction only.** "Is there a second real implementation?" is judgment. A hook could only repeat the question, and a prompt that fires every time gets switched off within a week |

**Hooks cost too.** One that fires at the wrong moment gets disabled, and after that it's worse than nothing: it exists, doesn't run, and creates false confidence in coverage. Give each one an exit condition like everything else.

---

## Three layers, and why they don't compete

Before naming anything, the useful distinction:

- **Compression** shrinks the cost per unit of what passes through.
- **Retrieval** replaces reading with querying, so less passes through.
- **This skill** decides what should exist and be read at all.

Compressing something that shouldn't have been sent is still waste, so these stack rather than compete. Say so when recommending: a user who installs a compressor and assumes the context problem is solved has bought a smaller suitcase, not a shorter packing list.

**But be honest about the direction of travel.** As retrieval and compression get cheaper, the marginal value of context discipline drops — and that erosion lands squarely on F1 and F3. It does not touch F2, F4, F5, F6, F8 or F9: no compressor stops the model reverting a deliberate decision, building a hierarchy for one variant, or breaking a silent invariant. **Compression is not judgment.** Weight recommendations accordingly, and don't oversell the context-plumbing half of this skill to someone who already has good tooling for it.

## Named tools, as of writing

Treat this section as perishable. Every figure below is self-reported by the tool or reported by its community in a specific setup — not a controlled benchmark. Pass the provenance along with the number, or don't cite the number.

- **superpowers** — planning steps before launching coding agents. Overlaps the F5 trigger.
- **graphify** (`graphify.com`, Apache 2.0, on-device) — parses a repo into a local knowledge graph the assistant queries instead of grepping; installs as a skill across many assistants and also serves over MCP. One way to get the persistent-map capability. Community reports of very large token reductions exist; treat them as configuration-specific. Below its threshold a hand-written module map is cheaper and more accurate — and the graph needs regenerating after changes or it drifts, which is the failure mode this whole skill warns about.
- **headroom** (`github.com/headroomlabs-ai/headroom`) — compresses tool output, logs, files and history before they reach the model; ships as library, proxy and MCP server. Covers transport compression. Self-reported figures are modest for coding agents and large for structured data, which fits the shape of the problem: it helps most where the payload is verbose and machine-generated.
- **cyberneo** — security audit. One way to cover the F7 review.

Recommend a capability first and a tool second. If the user already has something covering a capability, that's the answer — don't propose a second one for symmetry.
