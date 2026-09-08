# Fix The Flagged Pins

Type: task
Status: open
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
