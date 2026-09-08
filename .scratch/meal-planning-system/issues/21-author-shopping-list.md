# Author The Shopping-List Skill

Type: task
Status: open
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
