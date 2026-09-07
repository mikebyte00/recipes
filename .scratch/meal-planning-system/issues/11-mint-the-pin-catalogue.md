# Mint The Pin Catalogue

Type: grilling
Status: resolved
Blocked by: 09

## Question

Turn harvested products and hand-authored proteins into `PINS.md`.

[Where Everything Lives](05-where-everything-lives.md) gave the catalogue a
home and deliberately left it empty.
[How Ingredients Are Named](04-how-ingredients-are-named.md) settled what a Pin
*is*: a canonical ingredient bound to a purchasable product, declaring the one
unit its recipes must use, carrying pack size, a `staple` flag and
`alternates`.

Nothing owned building it. Two tickets now wait on it, which is why this
graduated from the map's fog.

### Inputs

- **86 distinct Waitrose products** with verified line numbers, captured in
  `Orders/` by the August harvest.
- **~7 proteins that can never be harvested** — chicken, eggs, steak and honey
  from Soutars; bream, bass and salmon from Dorset Meats. Neither sells online.
  These are authored by hand and cover every dinner in the corpus.

### Grill on

- **What a Pin record looks like.** Canonical name, product name, line number,
  pack size, declared unit, `store`, `staple`, `alternates`. One table, or one
  record per ingredient?
- **The declared unit.** `How Ingredients Are Named` says the Pin declares it
  and Recipes comply. Which unit wins when the corpus disagrees with the pack —
  cannellini beans are sold in a 400g can and written as `1 can`, `150g`,
  `240g` and `300g`?
- **Coverage.** How many of the corpus's canonical ingredients get a Pin from
  86 products, and what is left Unpinned? That number sizes
  [Normalise Ingredient Units](12-normalise-ingredient-units.md).
- **Staples.** Salt, pepper and all oils are confirmed staples. Which of the 86
  harvested products join them?

### Answered by Harvesting Past Orders — do not re-grill

[Harvesting Past Orders](09-harvesting-past-orders.md) resolved two of the
points that were listed here:

- **Non-recipe products** need no filter. Matching is **slug-driven**: the 112
  ingredient slugs are walked and a product sought for each, so toilet roll is
  never considered. Products matching no slug are reported as a short "bought,
  matched nothing" list — evidence, not candidates.
- **Coverage is measured.** 112 distinct slugs against 86 distinct products.
  Substring matching gives **43 candidates and 69 misses**, and ~10 of the 43
  are wrong or ambiguous (`honey` → Hot Honey Gochujang; `water` → "in Water";
  two each for cottage cheese, tartare sauce, white chocolate, lentils,
  potatoes, avocado). Every match is human-confirmed; none is auto-accepted.

It also fixed the record shape in part: a Pin carries **product, line number,
pack size, declared unit, `store`, `staple`, `alternates`, `confirmed`** — and
nothing countable, since purchase frequency and recency derive from `Orders/`.
An unconfirmed Pin lives in `PINS.md` alongside the rest; consumers filter on
`confirmed`.

**So this ticket's live questions are the record's file shape** (one table or
one record per ingredient) **and the declared unit**, where the corpus
disagrees with the pack.

---

## Answer

**The rules are settled here; the writing is split out to
[Confirm And Write The Pins](13-confirm-and-write-the-pins.md).** Resolved
07 September 2026.

### Two premises in this ticket were wrong

- **The record shape was never open.**
  [How Ingredients Are Named](04-how-ingredients-are-named.md) already fixed it:
  a single YAML file keyed by slug, carrying `display`, `store`, `unit`, `pack`,
  `search_term`, `line_number`, `alternates`, `staple`, and `each_g` where a
  recipe needs both count and mass. Plus `confirmed` from
  [Harvesting Past Orders](09-harvesting-past-orders.md). Nothing to decide.
- **Cannellini is written two ways, not four** — `1 can` twice, and 300g / 240g
  / 150g. Across the whole corpus **only 13 of 112 slugs carry more than one
  unit**, and most are staples drifting between an unquantified glug and grams.
  The normalisation job is far smaller than this ticket assumed.

### A finding

`curry-powder` is the **only** ingredient in the corpus marked `staple` in one
recipe and not another. Nine plausible staples — `soy-sauce`,
`balsamic-vinegar`, `dijon-mustard`, `vegetable-stock`, `vanilla-extract`,
`tomato-puree`, `honey`, `chili-powder`, `tarragon` — are never marked at all.
Direct evidence for moving the flag to the Pin, as
[How Ingredients Are Named](04-how-ingredients-are-named.md) intended.

### Decisions

1. **`unit` is how the recipe measures it; `pack` is how it is sold.** This
   **amends** [How Ingredients Are Named](04-how-ingredients-are-named.md),
   which set `cannellini-beans: unit: can` and quantified lists in cans. The
   corpus writes 150g, 240g and 300g of cannellini in three different meals and
   those are real cooking quantities; normalising them to whole cans makes the
   recipe lie. Aggregation still collapses to addition — everything is grams —
   and the pack division with a round-up happens **once per Pin at list time**,
   not per recipe. `can` remains the right unit where a thing is genuinely
   bought and used whole.

2. **Every slug gets a Pin except `water`.** It is `staple: true` in all five
   uses and not a purchasable thing; a row for it would say only "do not buy
   this". The near-duplicate slugs — `lemon`/`lemon-juice`,
   `spinach`/`baby-spinach`, `potatoes`/`new-potatoes`/`baby-potatoes`,
   `brown-rice`/`wholegrain-rice`, `parsley`/`dried-parsley`,
   `dried-herbs`/`dried-italian-herbs`, `lime`/`lime-juice` — are **left
   alone**. Some are genuinely different products carrying different line
   numbers in the order history; deciding which is which belongs to
   [Normalise Ingredient Units](12-normalise-ingredient-units.md), with the
   recipes in front of it.

3. **`search_term` is the harvested product name, verbatim.** Waitrose's own
   words for the product are the best search string available — the research
   found `Fage 2%` returns bathroom tissue where
   `Fage Total 2% Fat Natural Greek Yogurt Large` returns the product. Free for
   86 Pins, hand-written only for the ~7 counter proteins, which are never
   searched. It also keeps
   [The Query String Generator](10-the-query-string-generator.md) working when a
   line number goes stale.

4. **A hand-authored Pin is born `confirmed: true`.** The flag exists to stop a
   machine's guess being trusted, and there is no guess. Ticking a box to
   confirm your own sentence is ceremony, and ceremony is how a safeguard
   becomes a rubber stamp.

5. **Unpinned is the absence of a Pin, not a stored row.** A row with no
   product is a Pin that is not one, and the catalogue stops being a lookup
   table. The reasons — never found in an order, sold only at a counter — are
   recorded in the minting ticket's answer instead.

6. **This ticket decides; it does not mint.** ~55 confirmable matches, ~7
   hand-authored Pins and a staple pass over 112 slugs, where every match is
   human-confirmed per
   [Harvesting Past Orders](09-harvesting-past-orders.md). Running that review
   at the tail of a long session is how it becomes a rubber stamp. Split to
   [Confirm And Write The Pins](13-confirm-and-write-the-pins.md), which gets a
   checkable bar: every slug either Pinned or accounted for.
