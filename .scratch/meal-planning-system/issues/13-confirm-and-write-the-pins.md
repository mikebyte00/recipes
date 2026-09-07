# Confirm And Write The Pins

Type: task
Status: resolved
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

## Answer

**`PINS.md` is written: 94 Pins, 18 accounted-for absences, 112 slugs reached.**
Every match was proposed and confirmed by hand on 07 September 2026. The
matching and review procedure is now written into
[Orders/HARVEST.md](../../../Orders/HARVEST.md) as steps 6–9.

| | Count |
| --- | --- |
| Waitrose Pins with harvested line numbers | 62 |
| Counter proteins, hand-authored | 7 |
| Staples with no product harvested yet | 25 |
| **Pins** | **94** |
| Absences, each with a recorded reason | 18 |
| Harvested products binding to no slug | 24 |

### A Pin does not need a product

The sharpest finding, and it changed the shape of the catalogue.

`CONTEXT.md` defines a Staple as "**a Pin** flagged as a store-cupboard item",
while [Mint The Pin Catalogue](11-mint-the-pin-catalogue.md) ruled that Unpinned
is the absence of a row. Together those say `salt`, `olive-oil` and 23 others —
never seen in the three captured orders — get no row, so they have nowhere to
carry `staple: true`, so they land on the shopping list as Unpinned items
**every week**. Exactly what the flag exists to prevent.

Resolved by allowing a **product-less Pin**: store, unit, `staple: true`, no
`line_number` and no `search_term` until a harvest supplies them. The seven
counter proteins already proved the shape — bream will never carry a Waitrose
line number and is still a Pin. A Pin is a decision about an ingredient, and
"store-cupboard, do not shop for it" is a decision. `search_term` stays absent
rather than guessed, which costs nothing because a Staple is never searched.

### Conflicts were switches, not ties

All six contested slugs resolved on one observation: the three orders are dated
11, 25 and 31 August, and **every conflict is a switch over time**. So the rule
is **recency wins, loser becomes an `alternate`** — a switch is a decision
already made with real money.

| Slug | Kept | Alternate |
| --- | --- | --- |
| cottage-cheese | Longley Farm 250g (417999) | Essential 300g (016264) |
| tartare-sauce | Essential 290g (034638) | Waitrose 180g (933476) |
| white-chocolate | Green & Black's 90g (032753) | Cooks' 180g (746489) |
| **lentils** | **Merchant Gourmet 250g (054268)** | Epicure 400g (054002) |
| avocado | Ripe Avocados 2s (742393) | Avocado each (046734) |
| lemon | Duchy 3s (088911) | Cooks' 4s (088460) |

**`lentils` is the exception that proves the rule**: recency picks Epicure, but
the recipes read *"pre-cooked green or Puy"* at 250g, which is Merchant
Gourmet's exact product and pack. Explicit recipe text overrides recency. Both
halves of that are now in `Orders/HARVEST.md`.

`white-chocolate` corroborates rather than conflicts — the most recent purchase
is also the one matching the recipe's *"high-quality, e.g. Lindt"* note.

### Near-duplicate slugs share a line number

`spinach`/`baby-spinach`, `brown-rice`/`wholegrain-rice`,
`rocket`/`mixed-salad-greens`, `baby-potatoes`/`new-potatoes`, and
`lemon`/`lemon-juice` and `lime`/`lime-juice` each **Pin both members to the
same product**. It is honest — one product really does serve both words — it
keeps "every slug is Pinned" true, and the duplicate line numbers are the signal
that makes the pairs trivial to find. Collapsing the slugs stays
[Normalise Ingredient Units](12-normalise-ingredient-units.md)'s job, with the
recipes in front of it.

`lemon-juice` and `lime-juice` joined that set on the same logic: you squeeze
the fruit, and no bottled juice appears in any order.

### Judgement calls

- **`gochujang` → Cooks' Ingredients Hot Honey Gochujang (930008).** The
  product that made `honey` the textbook bad match is the *right* match here —
  it is the only gochujang bought and both uses are glazes. The failure was
  always the slug it got attached to. `display` says "Gochujang (hot honey)" so
  a list never implies plain gochujang.
- **`sourdough` → Light Rye Boule (841175).** Proposed as an absence, since the
  recipes say "seeded" and a rye boule is neither seeded nor sourdough. **The
  user overruled**: bread is bread, and some weeks it will not be seeded. Pinned,
  `display: Bread`.
- **`garlic-powder` → Cooks' Ingredients Garlic Granules (470588).** Granules,
  not powder; same aisle, same job.
- **`white-fish` stays one Pin.** The user does order bream and bass separately
  at the counter, but the recipes genuinely mean any white fish, so bream and
  bass are `alternates` rather than slugs.

### The staple ruling

The test: *something you expect to already have, and would not shop for in a
normal week.* **38 Pins carry `staple: true`.**

`curry-powder` — the corpus's only inconsistently-flagged ingredient — is a
Staple, and so are all nine the ticket listed as unflagged. Also stapled: the
jars that keep and get used in grams (peanut butter, harissa, hot sauce, peri
peri sauce, gochujang, both mayonnaises, butter, honey).

**`garlic`, `ginger` and `black-olives` were deliberately left unstapled**:
cupboard-adjacent but genuinely perishable, so they belong on a shopping list.
Since no product for them has been harvested either, they fall through to
absences — which is why the count is 94/18 and not the 97/15 first proposed.

### The 18 absences

`water` (not a purchasable thing, settled by
[Mint The Pin Catalogue](11-mint-the-pin-catalogue.md)); fourteen never
harvested — `blue-cheese`, `burger-buns`, `chestnut-mushrooms`,
`flaked-almonds`, `green-beans`, `halloumi`, `lettuce`, `parsley`, `pineapple`,
`red-onion`, `strawberries`, `waffle-fries`, `wholewheat-linguine`,
`milk-chocolate`; and `garlic`, `ginger`, `black-olives` as above.

`milk-chocolate` is the one worth knowing about: the only chocolates in the
history are dark (789167) and white. The Belgian Dark Chocolate is plausibly
what the strawberry pots use, but swapping a stated ingredient for a different
one on a hunch is what `confirmed` exists to prevent. Left absent.

### Bought, matched nothing

24 of 86 products bind to no slug — seven household and personal, seventeen
groceries outside the corpus. **Tenderstem broccoli** is the interesting one:
200g, bought twice, and no Recipe uses it. That reads like a dinner side cooked
regularly and never written down — a Recipe candidate, not a Pin.

### Left for other tickets

- **`staple: true` still sits on 33 recipe files**, now a second source of truth
  against the 38 Staple Pins. Stripping it is
  [Normalise Ingredient Units](12-normalise-ingredient-units.md)'s job, which
  this ticket unblocks.
- **Each Pin declares one `unit`**, chosen as the dominant unit its recipes use.
  Where the corpus disagrees — 13 of 112 slugs — the Pin now states the target
  and the recipes are the things that must move.
