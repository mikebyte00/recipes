# Fix The Flagged Pins

Type: task
Status: resolved
Blocked by: —

## Question

Four Waitrose Pins make `bin/shopping-list.py` emit `buy 1` with a warning
instead of a real pack count. All four appear in Menu 1's list.

| Pin | Defect |
| --- | --- |
| `sourdough` (displays as **Bread**) | no `pack` |
| `celery` | no `pack` |
| `spring-onions` | no `pack` |
| `oat-milk` | `unit: g` against `pack: 1 litre` |

The first three are a data gap: nobody recorded a pack size. The fourth is
wrong rather than absent — the Recipes measure oat milk in grams and the product
is sold by the litre, so there is no division to do without inventing a density.
Either the Pin's `unit` moves to `ml`, or the Recipes do, or the `pack` is
restated in grams. [Normalise Ingredient
Units](12-normalise-ingredient-units.md) moved Recipes and left Pins alone
because the Pins were confirmed by hand; that precedent points one way, but the
`1 litre` pack is the part that looks least deliberate.

Recorded as findings by [What The Four Skills
Are](08-what-the-four-skills-are.md) and made visible by [The Shopping List
Script](17-the-shopping-list-script.md), which flags rather than guesses. Fixing
them is a `PINS.md` edit and a re-run; the regression numbers in 17 must still
hold afterwards, except for the four rows that stop being flagged.

`garlic-mayonnaise` and `peri-peri-mayonnaise` have the same `g`-against-`ml`
shape but are Staples, so they never reach a list. Fix them or leave them, but
decide rather than skip.

## Answer

**All six fixed, and the `litre` unit is gone from the vocabulary.**
`bin/shopping-list.py` now emits **0 flags** on both Menus, and every regression
number from [The Shopping List Script](17-the-shopping-list-script.md) holds
unchanged: Menu 1 gives **39 shoppable lines** (34 Waitrose, 3 Soutars, 2 Dorset
Meats), **14 Unpinned**, 29 Staples left out; Menu 2 runs clean; **0 Recipe/Pin
rule violations across all 37 Recipes**.

| Pin | Fix |
| --- | --- |
| `sourdough` | `pack: { qty: 12, unit: slices }` |
| `celery` | `pack: { qty: 400, unit: g }` |
| `spring-onions` | `pack: { qty: 100, unit: g }` |
| `oat-milk` | `unit: ml`, `pack: { qty: 1000, unit: ml }`; `eggy-bread` moved 60 g → 60 ml |
| `garlic-mayonnaise` | `unit: g` → `ml` |
| `peri-peri-mayonnaise` | `unit: g` → `ml` |

**Measured before deciding, and it changed the framing.** Corpus demand for all
four flagged Pins is tiny and single-sited — bread 9 slices across a week, celery
**one** Recipe at 100g, spring onions **one** at 30g, oat milk **one** at 60g.
Every plausible pack figure gives `buy 1`, so **no value here is load-bearing at
a rounding boundary**. That is why hand-estimated pack sizes were acceptable at
all; a Pin whose division decided between one pack and three would have needed a
harvest, not an estimate.

**`litre` was a one-off.** Pack units ran 46 `g`, 4 `each`, 2 `ml` and **1
`litre`** — used by `oat-milk` alone. Restating it in `ml` retires a unit rather
than teaching the script a new conversion, which is why the fix is better than
`pack: { qty: 1000, unit: g }`: that second option needs no Recipe edit but
keeps a density lie in the file. Oat milk is ~1.03 g/ml, so `60g` → `60ml`
changes no arithmetic. Pack units are now `g` (48), `each` (4), `ml` (3),
`slices` (1).

**The precedent from [Normalise Ingredient
Units](12-normalise-ingredient-units.md) held**: the Recipe moved, the Pin's
`unit` moved only where it was describing a liquid as a solid. Three of the six
were a pure data gap — `pack` absent, nobody's decision — and needed a value,
not a ruling.

**`sourdough` is the one that bends a field.** `pack` means "how it is sold",
and a Light Rye Boule is not sold by the slice: 12 slices is a **yield**. It was
taken anyway, with the user's agreement, because the alternative — `pack: { qty:
1, unit: each }` — re-flags the row as a unit mismatch and fixes nothing, and
because bread at 9 slices a week is nowhere near a boundary. Recorded here so
the next person reading that row knows it is deliberate.

**The two mayos were fixed rather than left.** Both are `staple: true` and both
Recipe lines carry no `qty`, so they take rule 2's branch and never reach a
list — the defect was latent, not live. Fixing costs nothing precisely because
no `qty` exists to migrate, and it clears the last `g`-against-`ml` pair from
`PINS.md`.

**0 flags is exhaustive, not merely unexercised.** Checked across the whole
catalogue rather than across the two Menus: **no measured-unit-against-different-
pack-unit mismatch remains anywhere in `PINS.md`**, and of the 31 Pins still
carrying no `pack`, **25 are Staples** (never reach a list, `honey` among them — a Soutars Staple) and **6 are the
counter proteins** — `chicken-breast`, `chicken-thighs`, `eggs`, `salmon`,
`sirloin-steak`, `white-fish` — which are bought to weight or count at
Soutars and Dorset Meats and render with no Buy column at all. A missing `pack`
on a counter protein is correct, not a gap. So there is no Menu or Plan that can
make the script flag on today's corpus.

**Nothing new for the fog.** The four flags were the complete set the script
could raise on the current corpus, and it now raises none.
