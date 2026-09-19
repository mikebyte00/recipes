---
name: plan-the-week
description: "Plan a real week's food. Harvests last week's Waitrose order, builds Plans/YYYY-MM-DD.md from the browse page's Plan mode, edits it for the week actually happening — days away, Recipes swapped, Slots eaten out — generates the shopping list, then offers to fill the Waitrose trolley. Use when planning or re-planning a week, or when asked what the household is eating and buying."
---

# Plan the week

A **Plan** is one week actually happening — 28 Slots, built for that week and
kept. This skill assembles one and ends holding a shopping list.

Read `VOCABULARY.md` — *The Plan grid* — and `GOALS.md` before editing a grid.

## Steps

1. **Offer the harvest.** The order that just landed is *last* week's, so its new
   Pins serve *this* week. It is a browser session in the user's own signed-in
   account, following `Orders/HARVEST.md` — ask before opening one.

   A week that skips it still shops: this week's new ingredients come out
   **Unpinned**, which is the designed path, and the next harvest Pins them.

2. **Build the grid.** The browse page's **Plan mode** is where a week is
   chosen: it walks all 28 Slots against the pool and its checkout hands back a
   finished `days:` block. Ask the user to paste that block.

   `ls Plans/` says what the last few weeks ran — variety is measured against
   weeks actually eaten, so say what is still fresh before they start clicking.

   Name the file for the week's Monday — `date -d monday +%F` — and confirm that
   date with the user before writing. Paste the block in verbatim, all 28 Slots:

   ```markdown
   ---
   title: Week of 2026-09-14
   days:
     sunday:
       breakfast: <slug>
       ...
   ---
   ```

   A Plan stores its own **full resolved grid**, never a pointer to one
   elsewhere: nothing edited later may change what a past week says it ate.
   Overwriting an existing Plan is destructive — read it first.

   **A week that skips Plan mode** starts from a blank 28-Slot grid, every Slot
   written `eaten-out`, and fills it at step 3. That is the slower path and it
   is the one to offer only if they decline the page.

3. **Edit it into the real week.** The judgement step: ask what is different
   about this week, then make each difference one of three edits.

   | The week | The edit |
   | --- | --- |
   | Out for a meal | That Slot becomes `eaten-out` |
   | Fancies something else | That Slot takes another slug from `Recipes/` |
   | Cooks one batch across two meals | The **same slug in both Slots** |

   Every Slot keeps a value, so the grid stays at 28 — see [The grid stays
   whole](#the-grid-stays-whole). Notes about the week go **above** the
   `## Shopping` heading; everything below it is replaced at step 5.

   Wanting a Recipe the pool does not hold: **name the gap precisely** and point
   at `new-recipe`. `new-recipe` is the only writer to `Recipes/`.

4. **Sum the days and report.** Bands are checked at the day, not the Recipe.

   ```bash
   python3 - Plans/<Monday>.md <<'PY'
   import sys; sys.path.insert(0, 'bin')
   sl = __import__('shopping-list')
   front, grid = sl.load_grid(sys.argv[1])
   rec = sl.load_recipes('.', grid)
   day = {d: [0, 0, 0] for d in sl.DAYS}
   for d, _, v in grid:
       if v == sl.EATEN_OUT:
           day[d][2] += 1
           continue
       m = rec[v]['macros']
       day[d][0] += m['protein_g']; day[d][1] += m['kcal']
   for d in sl.DAYS:
       p, k, out = day[d]
       note = (f"  {out} Slot(s) eaten out -- not judged" if out else
               ("  UNDER the ~120g floor" if p < 120 else "")
               + ("  OVER the ~1800 kcal ceiling" if k > 1800 else ""))
       print(f"{d:<10} ~{p:g}g protein  ~{k:g} kcal{note}")
   PY
   ```

   Show the user every day that misses, and by how much. **Report, never block**
   — 6 of the 14 days the corpus was extracted from miss the floor by 0.5–7.5g,
   so a miss is the corpus talking, not the week going wrong. Offer a denser
   swap; take the week as it is if they decline.

   A day holding an `eaten-out` Slot is **not judged**: the household ate, just
   not from the grid, so its short total says nothing about the week.

5. **Generate the shopping list.** Invoke the `shopping-list` skill against the
   Plan you just wrote. It appends the `## Shopping` section and hands over the
   Multi-search block — this is the same skill the user re-runs on Wednesday
   when a Recipe changes.

6. **Offer to fill the trolley.** The Waitrose table is now final, and every row
   in it carries a line number — so the basket can be built directly, following
   `Orders/BASKET.md`. Like the harvest, it is a browser session in the user's
   own signed-in account: **ask before opening one**, and never place the order.

   Say what it covers before they answer: the pinned Waitrose lines only. The
   **Unpinned** items have no line number by definition and stay with the
   Multi-search block from step 5, as do Soutars and Dorset Meats, which are
   counter lists.

   Declining is a normal week. The Multi-search block is a complete way to shop
   on its own, and step 5 already handed it over.

**Done when** `Plans/<Monday>.md` holds 28 Slots, the user has seen every day
that misses a goal, and the file ends with a `## Shopping` section. Filling the
trolley is offered, never required — a week that declines it is finished.

## The grid stays whole

28 Slots, always. An emptied Slot or a deleted key reads
as an **incomplete** grid and `bin/shopping-list.py` treats it as fatal, so a
meal that is not being cooked is spelled `eaten-out`, the one reserved value.
It buys nothing.

There is no doubling control, and asking for one is a sign the grid is being
fought. Two Slots holding one slug **is** the doubled batch: the shopping list
adds quantities before it rounds up to packs, so it buys for four portions
whether they come from one pan or two.

## The macros are approximations

Write `~` on every macro figure shown to the user. Protein is a **floor** and
kcal a **ceiling** — being over on protein and under on calories costs nothing,
because carbohydrates and fat are untracked.
