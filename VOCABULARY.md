# Vocabulary

The closed value lists a Recipe's fields and a Plan's grid draw from. **Closed
means enforced: an unrecognised value is an error, not a new member.**

Decided in
[The Tag Vocabulary](.scratch/meal-planning-system/issues/03-the-tag-vocabulary.md),
which holds the reasoning. This file is the operative list.

| Field | Cardinality | Values |
|---|---|---|
| `slot` | one | `breakfast` `lunch` `dinner` `pudding` |
| `protein` | one, or absent on a pudding | `sausage` `egg` `tofu` `quorn` `chicken` `white-fish` `oily-fish` `beef` `dairy` `protein-powder` |
| `effort` | one | `low` `medium` `high` |
| `rating` | one, or absent | `1` `2` `3` `4` `5` |
| `appliances` | list | `skillet` `air-fryer` `ninja-sizzle` `rice-cooker` `pot` `toaster` `poacher` |
| `tags` | list | `fakeaway` `bulk-cook` `eat-cold` |

## Rules

1. **Extend on first real use**, as a one-line edit to this file. Values are not
   pre-stocked for recipes that do not exist. (`beans` is absent for this
   reason: every bean-titled recipe in the corpus turned out to be built on
   chicken.)
2. **`lower-kebab-case`** throughout, matching `ingredient:` keys and
   filename-as-identity.
3. **Tags are capability, never intent.** A tag says what a Recipe *can* do.
   What a given week did with it belongs to a Plan.

## Tags

- **`fakeaway`** — restaurant-style dish cooked at home. Independent of
  `protein`: chicken in menu 1, lemon sole in menu 2.
- **`bulk-cook`** — can be cooked 4+ portions in one go.
- **`eat-cold`** — fit to eat cold the next day, where no reheat is available.

**`bulk-cook` and `eat-cold` have no consumer.** They are labels a human reads.
Recipe generation, Menu building, weekly planning and the shopping list all
ignore them. Acting on either is a Plan-time decision, and a Plan spells it by
holding the **same Recipe in both Slots** — which sums to exactly one doubled
batch, because the shopping list adds quantities before it rounds up to packs.
See [How A Plan Records Bulk-Cook And
Eat-Cold](.scratch/meal-planning-system/issues/22-bulk-cook-and-eat-cold.md).

## The Plan grid

A Plan's grid holds the same 28 Slots as the Menu it came from. A Slot holds a
Recipe slug, or the one reserved value:

- **`eaten-out`** — the household did not cook this Slot. It buys nothing.

Keeping the Slot present is what lets the 28-Slot completeness check stay
meaningful: an empty value or a missing key reads as an incomplete grid, which
`bin/shopping-list.py` treats as fatal. Decided in
[The Shopping List Script](.scratch/meal-planning-system/issues/17-the-shopping-list-script.md).

**A Plan's body ends with its `## Shopping` section.** Regenerating the list
replaces everything from that heading to the end of the file, so anything
written below it is lost on the next run. Notes about the week go above it.


## Notes on three fields

**`protein` is omitted on a `pudding`** and required on every other slot.
`GOALS.md` lays out the week in protein types across breakfast, lunch and
dinner; puddings sit outside that layout, so a pudding has no protein type to
carry. A `dairy` value would be a type nothing plans against, and a later
session could read it as filling a slot.

**`protein` is single-valued** because the fakeaway burger carries chicken *and*
halloumi and the steak pilaf carries beef *and* parmesan, but `GOALS.md` counts
only one of them. It is **never inferred from a title** — one recipe in the
corpus is named for a bean and built on chicken.

`quorn` is retained with zero members today, an explicit exception to rule 1, so
a later session does not re-litigate whether Quorn counts as its own protein. It
must not be `chicken`: that would satisfy "1x Chicken Dinner" and silently
consume a meat slot.

**`effort` is written once when the Recipe is created and then stored, never
recomputed.** A value that changed between readings could not be planned
against. Judge it on pans and parallelism as much as ingredient count — a
nine-ingredient dish in one skillet is easier than an eight-ingredient dish
across three appliances.

- `low` — ~4 or fewer ingredients, 0–1 appliances.
- `medium` — 5–7 ingredients, 1–2 appliances.
- `high` — 8+ ingredients, or 3 appliances.

**`rating` is written by a human, never by an agent.** It records how good the
household found a Recipe once they had eaten it, which is not knowable at the
time it is authored. Unlike `effort` — Claude-generated and then stored — a
rating has no rule an agent could apply, so **a Recipe an agent writes omits
the field entirely** and the household adds a number later. Most of the pool is
unrated and will stay that way for a while.

Absent is not zero. `bin/browse.py` sorts unrated Recipes last under every sort
order, because a blank must not read as a bad score. Nothing else consumes the
field: Menu building, weekly planning and the shopping list all ignore it, and
it is the browse page's sort control alone that gives it a consumer.
