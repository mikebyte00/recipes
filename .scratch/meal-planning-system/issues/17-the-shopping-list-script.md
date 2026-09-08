# The Shopping List Script

Type: task
Status: resolved
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

## Answer

**`bin/shopping-list.py` is written, and it reproduces every regression number
exactly.**

```
Menu 1: 180 ingredient uses -> 63 quantified Pins -> 24 Staples dropped
        -> 39 shoppable lines (34 Waitrose, 3 Soutars, 2 Dorset Meats)
        -> 14 Unpinned
```

All four figures match [What The Four Skills
Are](08-what-the-four-skills-are.md) to the unit. Menu 2 runs clean on the same
code: 172 uses, 67 quantified Pins, 42 shoppable lines (36/4/2), 7 Unpinned.

**0 Recipe/Pin rule violations across all 37 Recipes.** The check
[Normalise Ingredient Units](12-normalise-ingredient-units.md) left unwritten is
now written, and the corpus passes it.

### The one shape this ticket had to decide

A Plan needs to say a Slot was not cooked, and [Where Everything
Lives](05-where-everything-lives.md) left the literal unwritten. It cannot be an
empty value or an omitted key, because those are indistinguishable from an
incomplete grid, which is a hard-fail.

**One reserved value, `eaten-out`.** Put to the user, who took one value rather
than a `skipped`/`eaten-out` pair. The Slot stays present, so the 28-Slot check
keeps meaning; it buys nothing; and no Recipe file can be named it, so it can
never collide with a slug. Written into `VOCABULARY.md` under **The Plan grid**,
because that file is the home of closed values and is where [Author The
Plan-The-Week Skill](20-author-plan-the-week.md) will look.

### Pack division, and the rule that stops it guessing

Twelve Pins have a `pack.unit` that differs from their `unit`. They split into
two kinds, and the split is what keeps the script from converting:

- **A countable container** — `chickpeas` is `can` against `410g`, `tofu` is
  `pack` against `200g`. **One recipe unit is one pack.** Nine Pins.
- **A measured amount against a different measure** — `g` against `ml` or
  `litre`. There is no division to do without inventing a density, so the row
  is **flagged**, never converted: `buy 1 ⚠ pack unit mismatch (g vs litre)`.

The rule is `unit in {g, ml}` decides which branch applies, so it needs no
hand-maintained list of container words.

### Where the script stops and the skill starts

The script **prints to stdout**; [Author The Shopping-List
Skill](21-author-shopping-list.md) writes the output into the Plan. That keeps
the script pure and runnable on anything, which is how Menu 1 was used as the
regression fixture — a Menu and a Plan carry the same `days:` grid, so the
script accepts either and reads `menu:` for provenance when it is there.

### Verified behaviours

| Behaviour | Result |
| --- | --- |
| Menu 1 / Menu 2 full run | 39 and 42 lines, counts as above |
| `eaten-out` on 3 Slots | 37 lines, reported in the summary |
| Grid missing 2 Slots | hard-fail, exit 1, both named |
| Slug resolving to no file | hard-fail, exit 1, slug named |
| `unit` disagreeing with its Pin | hard-fail, exit 1, recipe and Pin unit named |
| Non-staple with no `qty` | hard-fail, exit 1 |
| Missing `pack` | `buy 1 ⚠ pack unknown`, list still emitted |
| `g` against an `ml`/`litre` pack | `buy 1 ⚠ pack unit mismatch`, list still emitted |

### Findings, surfaced not fixed

Four Waitrose Pins degrade a real list today, and Menu 1 shows all four:
`sourdough` (displays as **Bread**), `celery` and `spring-onions` have no
`pack`; `oat-milk` is `unit: g` against `pack: 1 litre`. [What The Four Skills
Are](08-what-the-four-skills-are.md) recorded three of these as findings; the
script makes them visible in the output, which is the point of flagging rather
than guessing. Ticketed as [Fix The Flagged
Pins](23-fix-the-flagged-pins.md) rather than fixed in passing.

`garlic-mayonnaise` and `peri-peri-mayonnaise` share `oat-milk`'s `g`-against-
`ml` shape but are **Staples**, so they are dropped before pack division and can
never flag. Only `oat-milk` reaches the output.

### What this unblocks

[Author The Shopping-List Skill](21-author-shopping-list.md): the skill runs the
script, reads the flags and the Unpinned list, and writes the section into the
Plan. It adds judgement, not arithmetic.
