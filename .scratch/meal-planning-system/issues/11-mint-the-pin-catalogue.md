# Mint The Pin Catalogue

Type: grilling
Status: open
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
- **Non-recipe products.** The harvest captured the household shop — toilet
  roll, supplements, fruit no Recipe uses. Pinning those is wasted work, but
  the filter is a judgement that should be visible rather than silent.

Depends on the canonical-ingredient matching question in
[Harvesting Past Orders](09-harvesting-past-orders.md): `Epicure Organic
Cannellini Beans 400g` becoming `cannellini-beans` is the hard part, and
getting it wrong writes a bad Pin that then looks settled.
