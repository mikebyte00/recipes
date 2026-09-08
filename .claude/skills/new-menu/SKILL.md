---
name: new-menu
description: "Assemble a complete 28-Slot Menu from Recipes/ against GOALS.md's Weekly Layout, and write it to Menus/menu-N.md. Use when a new Menu is wanted — a third rotation, a themed week — or when the pool has grown enough to be worth reassembling one. Fails and names the exact gap when the pool cannot fill a Slot; never writes a Recipe itself."
---

# New menu

A Menu is **complete or it is not a Menu**: 28 Slots, every one a Recipe slug.
This skill assembles one from the pool against the Weekly Layout in
`GOALS.md` — read that section now if you have not already.

**It never calls `new-recipe`.** A Menu that cannot be filled fails and names
the gap precisely — *"needs a 3rd sausage breakfast under 490 kcal"*, never
*"pool too small"* — and hands that gap to the user, who decides whether to
grow the pool or fill the Slot some other way.

## Steps

1. **Name the file.** `ls Menus/` and take the next `menu-N.md`. Ask the user
   what this Menu is for — a plain third rotation, or a theme (Saturday's free
   dinner and the whole week's character both hang on the answer) — before
   assembling anything.

2. **See the pool by Slot and protein.** This is what step 3's fills draw from:

   ```bash
   python3 - <<'PY'
   import sys, glob, os; sys.path.insert(0, 'bin')
   sl = __import__('shopping-list')
   from collections import defaultdict
   by = defaultdict(list)
   for p in sorted(glob.glob('Recipes/*.md')):
       f = sl.load_frontmatter(p)
       slug = os.path.basename(p)[:-3]
       by[(f['slot'], f.get('protein'))].append(
           (slug, f['macros']['protein_g'], f['macros']['kcal'], f.get('tags') or []))
   for key, items in sorted(by.items()):
       slot, protein = key
       print(f"\n{slot} / {protein or 'no protein'} ({len(items)}):")
       for slug, p, k, tags in sorted(items, key=lambda x: -x[1]):
           print(f"  ~{p:g}g ~{k:g}kcal  {slug}" + (f"  [{','.join(tags)}]" if tags else ""))
   PY
   ```

3. **Fill the grid**, day by day, against the Layout. Six of the seven dinners
   are fixed by day; everything else is a floor or a count. Prefer the densest
   Recipe in each protein group first — the fills in `GOALS.md`'s worked
   Menus were chosen that way, and it is what keeps a day clear of the ~130g
   floor. Repeats within a Menu are normal, not a defect: the pool is thinner
   than 28, puddings most of all.

   | Slot | Rule |
   | --- | --- |
   | Breakfast | 7 total: 3 `sausage`, 4 `egg` |
   | Lunch | 7 total: `tofu` or `chicken`, **at least 2 of each** — a floor, not a ratio |
   | Dinner | Sun & Mon `white-fish` · Tue `chicken` · Wed `oily-fish` · Thu `beef` · Fri tagged `fakeaway` (any protein) · **Sat free** — your choice, whatever the week is thinnest on |
   | Pudding | 7, nightly, no protein type — draw from the whole pudding pool |

   A Slot the pool cannot cover **stops the skill**: state which day, which
   Slot, and the constraint that has no match — e.g. *"Wednesday dinner needs
   an `oily-fish` Recipe; the pool has 2 and both are already used elsewhere
   this Menu"* is not a stop, a genuinely empty group is. Report it to the user
   and wait; do not substitute a Recipe that breaks the rule to make 28 land.

4. **Write `Menus/menu-N.md`.** `days:` holds slug references only — no prose
   inside it, matching `menu-1.md` and `menu-2.md`:

   ```yaml
   ---
   title: Menu N
   days:
     monday:
       breakfast: <slug>
       lunch: <slug>
       dinner: <slug>
       pudding: <slug>
     ...
   ---
   ```

   Omit `source:` — that field marks a Menu extracted from the original
   `Rotations/` corpus, and this one is not. Prose about the week's character,
   if any, goes below the closing `---`.

5. **Check it and report.** Reuses `bin/shopping-list.py`'s own loaders — a
   Menu's `days:` grid is exactly the shape `load_grid` expects:

   ```bash
   python3 - Menus/menu-N.md <<'PY'
   import sys; sys.path.insert(0, 'bin')
   sl = __import__('shopping-list')
   path = sys.argv[1]
   front, grid = sl.load_grid(path)          # raises if short of 28 Slots
   recipes = sl.load_recipes('.', grid)      # raises if a slug resolves to no file
   sl.check_rule(recipes, sl.load_pins('.')) # raises on a Recipe/Pin rule violation
   day = {d: [0, 0] for d in sl.DAYS}
   for d, _, slug in grid:
       m = recipes[slug]['macros']
       day[d][0] += m['protein_g']; day[d][1] += m['kcal']
   for d in sl.DAYS:
       p, k = day[d]
       note = ("  UNDER the ~130g floor" if p < 130 else "") + \
              ("  OVER the ~1800 kcal ceiling" if k > 1800 else "")
       print(f"{d:<10} ~{p:g}g protein  ~{k:g} kcal{note}")
   PY
   ```

   An exception here is fatal: an incomplete grid, a slug with no Recipe file,
   or a Recipe/Pin rule violation. Fix it and run again.

   **Report, never re-fill on your own.** Show the user every day that misses
   the floor or breaches the ceiling, same as `plan-the-week` does for a real
   week — a Menu is not rejected for missing a rough objective, and the corpus
   itself misses on 6 of 14 existing days. Offer a denser swap if one exists in
   the pool; take the Menu as it is if the user declines.

**Done when** `Menus/menu-N.md` holds 28 Slots, the check above exits clean,
and the user has seen every day that misses a goal.

## Lunch is a floor, not a ratio

`GOALS.md` states this once and it is easy to over-apply: 2 tofu / 2 chicken is
the **minimum**, not a target to hit exactly. `menu-1.md` runs 4 chicken / 3
tofu and `menu-2.md` runs 5 tofu / 2 chicken — both satisfy the floor while
leaning hard in opposite directions, and that variance is fine.

## Saturday is the free dinner

Every other day's protein type is spoken for once already — a third white
fish, a second oily fish or steak, or a fourth chicken (counting Friday's
Fakeaway if it lands on chicken) all repeat a type inside one Menu. Pick
whatever the week is thinnest on, and let that thinness be a reason, not
a coin flip.
