# The Shopping List Script

Type: task
Status: open
Blocked by: 22

## Question

Write `bin/shopping-list.py`, the only code in this repo.

Authorised by [What The Four Skills Are](08-what-the-four-skills-are.md), which
holds the full ruling. **No other `bin/` entry is authorised by it.**

Reads `PINS.md`, `Recipes/` and a Plan. Aggregates each ingredient across the
Plan's resolved grid, divides into packs with `ceil()`, splits by `store`, drops
Staples, and emits the shopping section for the Plan.

- **Hard-fail** on a Recipe/Pin rule violation — an ingredient line whose `unit`
  disagrees with its Pin, or a slug resolving to no file — and on a Menu or Plan
  that is not 28 complete Slots. Non-zero exit.
- **Fall back and flag** on a missing `pack`: `buy 1` with `⚠ pack unknown`.
- **Unpinned ingredients** get their own headed list. Never guessed.
- Waitrose output carries a pasteable `search_term` block plus `line_number` per
  row; Soutars and Dorset Meats are plain quantities.

`line_number` is a **string** — `088460` is not `88460`.

Measured against Menu 1 while resolving 08: 180 ingredient uses, 63 quantified
Pins, 24 dropped as Staples, **39 shoppable lines** (34 Waitrose, 3 Soutars,
2 Dorset Meats), 14 Unpinned. That is the regression target.

Blocked because [How A Plan Records Bulk-Cook And Eat-Cold](22-bulk-cook-and-eat-cold.md)
decides whether a Plan slot carries a multiplier, which changes what this
aggregates.
