# The Snack Slot

Type: decision
Status: resolved
Blocked by: —

## Question

Batch bakes — mostly 8 servings — are cooked on the odd day and eaten through
the week. A Plan had nowhere to put one: a meal Slot buys a batch per Slot and
counts the whole batch's macros on one day.

## Answer

**A fifth, optional Slot, `snack`, meaning the day the batch is baked.** It
buys one batch; its macros spread evenly over the seven days from it, clipped
at the Plan's Sunday, overlapping batches adding. A snack Recipe carries
`makes:`, whole-batch quantities and per-serving macros — the one exception to
Serves 2. The full design is
[the snack Slot spec](../../../docs/superpowers/specs/2026-10-11-snack-slot-design.md).

### What changed

- `bin/shopping-list.py`: the grid's optional `snack:` key, `check_makes`, and
  `day_macros` — the one place the spread is computed.
- `bin/browse.py`: reads day totals from `day_macros` (its own `day_totals` is
  gone), a Snack group, a snack line per day, and a skippable snack step in
  Plan mode.
- `VOCABULARY.md`, `CONTEXT.md`, `CLAUDE.md`, `plan-the-week`, `new-recipe`.

### Not done

- No snack Band in `GOALS.md` until a few snacks exist to measure.
- A batch *breakfast* still buys a batch per Slot.
- A late-week bake's spread is not carried into the next Plan.
