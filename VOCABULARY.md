# Vocabulary

The closed value lists a Recipe's fields draw from. **Closed means enforced: an
unrecognised value is an error, not a new member.**

Decided in
[The Tag Vocabulary](.scratch/meal-planning-system/issues/03-the-tag-vocabulary.md),
which holds the reasoning. This file is the operative list.

| Field | Cardinality | Values |
|---|---|---|
| `slot` | one | `breakfast` `lunch` `dinner` `pudding` |
| `protein` | one | `sausage` `egg` `tofu` `quorn` `chicken` `white-fish` `oily-fish` `beef` |
| `effort` | one | `low` `medium` `high` |
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

## Notes on two fields

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
