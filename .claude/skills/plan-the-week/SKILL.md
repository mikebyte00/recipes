---
name: plan-the-week
description: "Plan a real week's food. Harvests last week's Waitrose order, copies a Menu's grid into Plans/YYYY-MM-DD.md, edits it for the week actually happening — days away, Recipes swapped, Slots eaten out — then generates the shopping list. Use when planning or re-planning a week, or when asked what the household is eating and buying."
---

# Plan the week

A **Menu** is an idea of a week. A **Plan** is the week actually happening. This
skill turns one into the other and ends holding a shopping list.

Read `VOCABULARY.md` — *The Plan grid* — and `GOALS.md` before editing a grid.

## Steps

1. **Offer the harvest.** The order that just landed is *last* week's, so its new
   Pins serve *this* week. It is a browser session in the user's own signed-in
   account, following `Orders/HARVEST.md` — ask before opening one.

   A week that skips it still shops: this week's new ingredients come out
   **Unpinned**, which is the designed path, and the next harvest Pins them.

2. **Choose the Menu.** `ls Menus/`, and ask which. `ls Plans/` says what the
   last few weeks ran — variety is measured against weeks actually eaten, so
   offer the Menu the household has had least recently.

3. **Copy the grid.** A Plan stores its own **full resolved grid**, never a diff:
   a Menu edited next month must not change what this week appears to say.

   Name the file for the week's Monday — `date -d monday +%F` — and confirm that
   date with the user before writing.

   ```bash
   MENU=Menus/menu-1.md MONDAY=2026-09-14; mkdir -p Plans
   { echo '---'; echo "title: Week of $MONDAY"; echo "menu: $MENU"; \
     awk '/^days:/{f=1} f&&/^---$/{exit} f' "$MENU"; echo '---'; echo; } > "Plans/$MONDAY.md"
   ```

   `awk` lifts the grid **verbatim**, so all 28 Slots arrive without passing
   through you. Overwriting an existing Plan is destructive — read it first.

4. **Edit it into the real week.** The judgement step: ask what is different
   about this week, then make each difference one of three edits.

   | The week | The edit |
   | --- | --- |
   | Out for a meal | That Slot becomes `eaten-out` |
   | Fancies something else | That Slot takes another slug from `Recipes/` |
   | Cooks one batch across two meals | The **same slug in both Slots** |

   Every Slot keeps a value, so the grid stays at 28 — see [The grid stays
   whole](#the-grid-stays-whole). Notes about the week go **above** the
   `## Shopping` heading; everything below it is replaced at step 6.

   Wanting a Recipe the pool does not hold: **name the gap precisely** and point
   at `new-recipe`. `new-recipe` is the only writer to `Recipes/`.

5. **Sum the days and report.** Bands are checked at the day, not the Recipe.

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
               ("  UNDER the ~130g floor" if p < 130 else "")
               + ("  OVER the ~1800 kcal ceiling" if k > 1800 else ""))
       print(f"{d:<10} ~{p:g}g protein  ~{k:g} kcal{note}")
   PY
   ```

   Show the user every day that misses, and by how much. **Report, never block**
   — 6 of the 14 days across the two Menus already miss the floor by 0.5–7.5g,
   so a miss is the corpus talking, not the week going wrong. Offer a denser
   swap; take the week as it is if they decline.

   A day holding an `eaten-out` Slot is **not judged**: the household ate, just
   not from the grid, so its short total says nothing about the week.

6. **Generate the shopping list.** Invoke the `shopping-list` skill against the
   Plan you just wrote. It appends the `## Shopping` section and hands over the
   Multi-search block — this is the same skill the user re-runs on Wednesday
   when a Recipe changes.

**Done when** `Plans/<Monday>.md` holds 28 Slots, the user has seen every day
that misses a goal, and the file ends with a `## Shopping` section.

## The grid stays whole

28 Slots, always — a Menu's shape, kept. An emptied Slot or a deleted key reads
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
