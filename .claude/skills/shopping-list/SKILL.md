---
name: shopping-list
description: "Generate or regenerate a Plan's shopping section — the per-store lists, the Waitrose Multi-search block to paste, and the Unpinned items to add by hand. Use whenever a Plan is written or changes: a Recipe swapped, a Slot eaten out, or the list simply wanted again."
---

# Shopping list

`bin/shopping-list.py` does every sum and every pack division. You choose the
Plan, read what the script flags, and put it in front of the user.

**Re-runnable by design.** A Wednesday swap gets a fresh list without re-running
the planning conversation — that is the whole reason this is not part of
`plan-the-week`.

## Steps

1. **Pick the Plan.** Named by the user, else the newest `Plans/*.md`. Say which
   one you picked. If `Plans/` holds nothing, the week has not been planned yet:
   say so and point at `plan-the-week`, which is what creates one.

2. **Run it and read the output.**

   ```bash
   python3 bin/shopping-list.py Plans/<date>.md
   ```

   Exit 1 is a hard failure — a Recipe's `unit` disagreeing with its Pin, a slug
   resolving to no Recipe file, or a grid short of 28 Slots. The sum would be
   meaningless. Report the message, fix the cause with the user, run again.

3. **Write the section into the Plan.** `## Shopping` is the Plan's **last**
   section, so regenerating means replacing from that heading to the end of the
   file:

   ```bash
   { awk '/^## Shopping$/{exit} {print}' Plans/<date>.md | sed -E '${/^$/d;}'; echo; \
     python3 bin/shopping-list.py Plans/<date>.md; } > /tmp/plan.md \
     && mv /tmp/plan.md Plans/<date>.md
   ```

   Re-running the script is what makes the section **verbatim by construction**:
   the numbers reach the file without passing through you. `sed` then `echo`
   leave exactly one blank line before the heading however many times you run
   it, and `mv` runs only on success — so a hard failure at step 2 leaves the
   Plan holding the section it already had.

4. **Report the judgement.** Three things, in the user's reply:
   - Every **⚠** row, each with the Pin to fix in `PINS.md` (see [Flags](#flags)).
   - The **Unpinned** list — the items they add by hand.
   - The line count and the store split, so they know the size of the shop.

   Then hand them the **Multi-search block** to paste, and the **counts block**
   under it — Multi-search adds 1 of each and carries no quantity, so the counts
   are a second pass they make by hand. Both come from the script; do not retype
   either.

**Done when** the Plan on disk ends with the script's current output, and the
user has seen every ⚠ and every Unpinned item.

## Flags

A **⚠** is a data gap in `PINS.md`, not an error: the line falls back to `buy 1`
and the week still shops.

| Flag | Fix |
| --- | --- |
| `pack unknown` | Add `pack:` to that Pin — how the product is **sold** |
| `pack unit mismatch` | The Pin's `unit` and its `pack` unit measure different things. Restate one of them; convert neither |

Both are one-line `PINS.md` edits. **Ask the user for the pack size** — it is a
fact about a product they buy — then apply it and re-run. Every Pin the corpus
reaches divides cleanly today, so a ⚠ means a Pin that is new or newly edited.

## Unpinned

No Pin exists for these, so the script leaves them off the store lists rather
than guessing a product. Buying one puts it in the order history, where the next
harvest turns it into a Pin. This is the designed path, not a backlog — leave
the Pin to the harvest.

## Waitrose

**Hand over search terms; the user pastes them.** This skill does not drive the
basket and does not place orders — a decision backed by research, in
`CLAUDE.md` and [Can Claude Drive
Waitrose](../../../.scratch/meal-planning-system/issues/01-can-claude-drive-waitrose.md).

Each row also carries its 6-digit `line_number`, which is the escape hatch when
a search term misfires: `/ecom/products/x/<line_number>` resolves on its own.

Soutars and Dorset Meats are counters. They render as plain quantities, with no
line numbers and no pack division, and you take that list to the shop.

## The section is the review step

The user reads the table and the Unpinned list **before** anything is pasted.
Write the output into the Plan and show it, rather than summarising it: a wrong
sum makes a wrong shop, and nothing downstream catches that.
