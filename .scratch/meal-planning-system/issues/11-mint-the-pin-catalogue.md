# Mint The Pin Catalogue

Type: grilling
Status: open
Blocked by: 09 (resolved — unblocked)

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
