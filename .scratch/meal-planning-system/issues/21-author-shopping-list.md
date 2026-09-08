# Author The Shopping-List Skill

Type: task
Status: resolved
Blocked by: 17

## Question

Write `.claude/skills/shopping-list/SKILL.md` — the thin one.

Runs `bin/shopping-list.py` against a Plan and writes the result back as a
regenerated section of `Plans/YYYY-MM-DD.md`. Puts the Unpinned list in front of
the user and hands them the Multi-search block to paste.

**It exists separately from `plan-the-week` because it is re-runnable**: a
Wednesday swap needs the list redone without re-running the planning
conversation. That is the whole reason for the seam — see
[What The Four Skills Are](08-what-the-four-skills-are.md).

It **generates search terms for the user to paste**. It does not drive the
basket and does not place orders. Read `CLAUDE.md` and
[Can Claude Drive Waitrose](01-can-claude-drive-waitrose.md) before extending it.

## Answer

**`.claude/skills/shopping-list/SKILL.md` is written, and every step of it was
run end to end before it was called done.** 95 lines: four steps, three
reference sections. `.claude/` did not exist before this ticket.

### It is model-invoked

The one invocation decision the ticket left open. `shopping-list` is the skill
you reach for **mid-week, in a session about something else** — "I swapped
Wednesday's dinner" — which is exactly the case autonomous discovery pays for,
and it is the same re-runnability that earned the seam in [What The Four Skills
Are](08-what-the-four-skills-are.md). It also leaves
[Author Plan-The-Week](20-author-plan-the-week.md) **free to chain into it or to
hand off to the user**, rather than binding that choice now. The price is one
always-loaded description; against four skills total, that is cheap.

### Three decisions the authoring forced

**`## Shopping` is a Plan's last section.** Regenerating is then one
deterministic operation — replace from the heading to end of file — with no
parser and no markers. Written into `VOCABULARY.md` beside The Plan grid, where
[Author Plan-The-Week](20-author-plan-the-week.md) will find it, because it
constrains where that skill may put notes about the week.

**The section reaches the file verbatim by construction.** The splice re-runs
the script and appends its stdout, so the numbers never pass through the agent.
Transcription was the one place a wrong sum could still enter a corrected
pipeline, and this closes it.

**Flags ask rather than estimate.** A `pack unknown` is a fact about a product
the user buys. [Fix The Flagged Pins](23-fix-the-flagged-pins.md) is the
precedent: the pack sizes there were only safe because they were confirmed, and
that ticket's own answer says a load-bearing division needs a harvest, not a
guess.

### Verified, not assumed

Ran against a throwaway Plan in the scratchpad rather than minting a real one —
writing `Plans/` is [Author Plan-The-Week](20-author-plan-the-week.md)'s job.

- **The splice is idempotent** across three consecutive runs, from both starting
  states (a Plan with no section, and a Plan with one).
- **A hard failure leaves the Plan untouched.** Forced one with a slug resolving
  to no Recipe file: exit 1, the message printed, `mv` never reached, the file
  byte-identical.
- **`eaten-out` works in a Plan**, which had never been exercised outside a
  Menu. Two Saturday Slots out took Menu 1 from 39 lines to **37**, and the
  summary line reported `2 Slot(s) eaten out`.
- **Zero flags**, as [Fix The Flagged Pins](23-fix-the-flagged-pins.md) left it.

**Two defects were caught by running it, both invisible on the page.** The first
splice ate the blank line before the heading and, being idempotent, would have
kept it wrong forever; `sed` then `echo` now normalise it whatever the starting
state. And the `description` **failed to parse as YAML** — an unquoted `: `
mid-sentence — so the skill would have been silently unloadable. That lesson is
now a standing line in the map's Notes rather than repeated on three tickets.

### Nothing new for the fog

The three remaining authoring tickets were already sharp, and this one narrowed
none of them.
