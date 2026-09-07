# Confirm And Write The Pins

Type: task
Status: open
Blocked by: 11

## Question

Write `PINS.md`: propose every match, confirm each one by hand, and account for
every slug that gets no Pin.

Split out of [Mint The Pin Catalogue](11-mint-the-pin-catalogue.md), which
settled the rules. Nothing here is a decision — it is the review that
[Harvesting Past Orders](09-harvesting-past-orders.md) made the safeguard, and
it needs a session of its own so it is not rubber-stamped at the tail of one.

### Inputs

- **86 distinct Waitrose products** with verified line numbers, in `Orders/`.
- **112 distinct ingredient slugs** across the 37 Recipes.
- Substring matching gives **43 candidates and 69 misses**; ~10 of the 43 are
  wrong or ambiguous. Measured in
  [Harvesting Past Orders](09-harvesting-past-orders.md); do not re-derive.

### The rules already settled

- Matching is **slug-driven**. Products matching no slug are reported as a
  "bought, matched nothing" list, never proposed.
- **Every machine-proposed match is confirmed by a human** before it is
  trusted. `confirmed: false` until then; consumers of Pins filter on it.
- A **hand-authored** Pin is born `confirmed: true`.
- **`unit` is how the recipe measures it; `pack` is how it is sold.**
- **Unpinned is the absence of a Pin.** No placeholder rows.
- `search_term` is the harvested product name, **verbatim**.
- Record shape from [How Ingredients Are Named](04-how-ingredients-are-named.md),
  plus `confirmed`.

### The work

- Propose a match for each of the 112 slugs against the 86 products, and put
  every one in front of the user. Expect ~55 proposals.
- Resolve the known conflicts: cottage cheese (Essential 300g vs Longley Farm
  250g), tartare sauce (Essential 290g vs Waitrose 180g), white chocolate
  (Cooks' 180g vs Green & Black's 90g), lentils, potatoes, avocado, lemons.
  The loser becomes an `alternate`.
- Reject the known-bad matches outright: `honey` → Hot Honey Gochujang;
  `water` → "in Water" / Watercress. **`water` gets no Pin.**
- Hand-author the ~7 counter proteins — chicken, eggs, steak and honey from
  Soutars; bream, bass and salmon from Dorset Meats. They cover every dinner in
  the corpus and can never be harvested.
- **Set `staple` per Pin.** Confirmed members: salt, pepper, all oils including
  truffle. `curry-powder` is the corpus's only inconsistently-flagged
  ingredient, and nine plausible staples are unflagged entirely —
  `soy-sauce`, `balsamic-vinegar`, `dijon-mustard`, `vegetable-stock`,
  `vanilla-extract`, `tomato-puree`, `honey`, `chili-powder`, `tarragon`. Rule
  on each.
- Record the "bought, matched nothing" list. Tenderstem broccoli and Cooks'
  Ingredients Basil are both in it.

### Done when

**Every one of the 112 slugs is either Pinned or accounted for in this ticket's
answer**, with the reason it has no Pin. Not "most of them".

`Orders/HARVEST.md` documents capture only; the matching and review steps have
no written procedure yet. Extend it or write a sibling.
