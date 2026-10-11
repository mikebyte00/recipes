# Snack Slot — Design

Date: 2026-10-11
Status: approved in conversation; awaiting spec review

## Goal

Give the household a fifth, optional Slot for **snacks**: batch-baked Recipes
(mostly 8 servings) that are cooked on the odd day and eaten through the week.
Most days have no snack. The Plan must buy one batch per bake, and the day
totals must reflect the batch being eaten across the week rather than all on
the baking day.

## Decisions

| Question | Answer |
|---|---|
| What a snack Slot means | **The day the batch is baked.** It buys one whole batch. |
| How a batch counts toward day totals | **Spread evenly over the 7 days from the bake day**, assuming the whole batch is eaten. Days past the Plan's Sunday are not shown. Overlapping batches add. |
| How the grid holds it | **An optional `snack:` key per day.** Absent means no snack. The four meal Slots stay required. |
| Batch size | **A `makes:` field** on snack Recipes. Quantities are for the whole batch; `macros` are per serving. |

## 1. Recipes

- `VOCABULARY.md`: `slot` gains `snack`. `protein` becomes "one, or absent on a
  pudding **or snack**". A new field:

  | Field | Cardinality | Values |
  |---|---|---|
  | `makes` | a positive integer, **required on a snack**, absent otherwise | servings per batch |

- A snack Recipe's ingredient `qty` values are for **the whole batch**, and its
  `macros` are **per serving**. This is a deliberate, scoped exception to
  *Serves 2*: `CLAUDE.md`'s standing constraint gains one line saying so.
- `CONTEXT.md` *Slot*: add snack, defined as a batch baked on the day it sits
  in, eaten across the week.
- `GOALS.md` gets **no snack Band** yet. There is no corpus to measure a range
  from; a Band is added once a few snacks exist. `bin/browse.py` already shows
  no Band row when a Slot has none.
- Snack Recipes live in `Recipes/` like every other Recipe.

**Validation.** `bin/shopping-list.py`'s Recipe checks reject a `slot: snack`
Recipe with no `makes:` (or a non-positive one), and reject `makes:` on any
other Slot. The `new-recipe` skill's vocabulary check gains `snack` and the
same `makes` rule.

## 2. The Plan grid

```yaml
days:
  wednesday:
    breakfast: <slug>
    lunch: <slug>
    dinner: <slug>
    pudding: <slug>
    snack: <slug>      # optional; omitted on a day with no snack
```

- `load_grid` keeps requiring the 28 meal Slots exactly as now, and
  additionally yields `(day, "snack", slug)` for any day that carries one.
  `snack: eaten-out` is rejected: a day without a snack simply omits the key.
- **Shopping:** unchanged arithmetic. Each snack Slot contributes its Recipe's
  batch quantities once, so baking the same snack twice in a week buys two
  batches.
- `VOCABULARY.md` *The Plan grid* gains a paragraph: 28 required Slots, plus an
  optional `snack` per day.
- Past Plans need no edit.

## 3. Day totals

A batch baked on day *D* adds, per person, to each of the 7 days *D … D+6*:

```
share = makes / 2 × per-serving macro / 7
```

Only days inside the Plan's own week (Monday–Sunday) are shown; the rest of a
late-week batch's spread falls outside the Plan and is not carried into the next
one. Several batches overlapping on a day add together.

*Example:* `makes: 8`, ~10g / ~150 kcal per serving, baked Wednesday →
~5.7g / ~86 kcal per person on each of Wednesday–Sunday.

**One implementation.** `bin/shopping-list.py` gains `day_macros(grid, recipes)`
returning, per day, the meal totals plus the snack share. It is the one place
the spread is computed:

- the `plan-the-week` skill's step 4 snippet is replaced by a call to it;
- `bin/browse.py` imports it (it already reads the same Plans and Recipes)
  instead of keeping a second copy, and its own `day_totals` stops counting the
  `snack` key as a meal.

A day's judgement is unchanged otherwise: a day holding an `eaten-out` meal is
still not judged, and the snack share is included in the totals of days that
are.

## 4. The browse page

- **Recipe list:** a *Snack* group after *Pudding*. Rows show macros per
  serving and a `makes 8` note.
- **Recipe page:** says "Makes 8 · macros per serving · quantities for the
  whole batch".
- **Plan mode:** after each day's pudding the walk offers a **snack** step.
  **Skip** is the expected answer and leaves no snack. The progress count and
  Checkout's enablement stay on the 28 meal Slots, so an all-skipped week checks
  out as today. Checkout's `days:` block writes a `snack:` line only for a day
  that has one, and its readable week shows it.
- **Plan page:** each day lists its snack under pudding when it has one, and its
  totals include the snack share, with a one-line note naming which bakes
  contributed.
- **Staples to check** includes snack Recipes, as it already counts every Slot.
- **Variety:** a snack's *last eaten* date is its bake day.

## 5. Skills and docs

- `plan-the-week`: the grid example shows the optional `snack:` key; step 4
  uses `day_macros`; *The grid stays whole* says snacks are the one optional
  Slot.
- `new-recipe`: the bar table gains a *Snack* row ("measured when the first few
  exist"); step 4's template documents `makes:`; the check script gains `snack`
  and the `makes` rule.
- `CLAUDE.md`: the *Serves 2* line notes the snack exception.
- A ticket, `issues/26-the-snack-slot.md`, records the decision against the
  map, linking this spec.

## 6. Testing

- `bin/shopping-list.py`: a grid with and without `snack` keys loads; a missing
  meal Slot still fails; `snack: eaten-out` fails; a snack Recipe without
  `makes` fails; a snack Slot buys exactly one batch; `day_macros` spreads a
  Wednesday bake over Wednesday–Sunday with the worked example's figures, a
  Sunday bake to Sunday only, and two overlapping bakes add.
- `bin/browse.py`: payload day totals match `day_macros`; the snack group
  renders; Plan mode skips snack without blocking Checkout and writes the
  `snack:` line only when set (node-driven, like the existing Checkout tests).
- The real-repo tests keep passing on the three existing Plans unchanged.

## Out of scope

- Moving the Brownie Bar to snacks, or a `makes:` field on breakfasts. A batch
  breakfast still buys a batch per Slot; that is a separate fix.
- Carrying a late-week batch's spread into the next Plan.
- A snack Band in `GOALS.md` (added once a few snacks exist).
