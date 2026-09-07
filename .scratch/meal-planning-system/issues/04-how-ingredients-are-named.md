# How Ingredients Are Named

Type: grilling
Status: resolved
Blocked by: 01, 02

## Question

How are ingredients named and structured so a shopping list can aggregate them?

This is the hinge of the whole system. Across a week, "chickpeas" appears in
several Recipes as "1 can drained chickpeas" and must come out the far end as
one line: `Chickpeas, 2 cans, Waitrose`. That demands a canonical name, a unit
that survives addition, and a Store.

Grill on:

- Does a canonical ingredient catalogue exist as its own set of files, or is
  the canonical name just a string Recipes agree to spell identically?
- Where does Store routing live — on the ingredient, or decided at list time?
  Eggs come from Soutars and fish from Dorset Meats, and that is stable.
- How do incompatible units add up? 150g cherry tomatoes plus "1 punnet".
- What happens to the store-cupboard items — 5g truffle oil, a pinch of salt —
  that the old CSV listed anyway but you clearly do not rebuy weekly.

What [Can Claude Drive Waitrose](01-can-claude-drive-waitrose.md) finds changes
this: a stable product ID from past orders means an ingredient record can point
straight at a purchasable thing.

## Settled while charting

Do not re-litigate these; they came from the user directly.

- Pins are **stored in the repo**, not re-derived from order history each run.
- A Pin carries: canonical name, display name, Store, **pack size and unit**,
  product identifier, alternates for substitutions, and a **staple** flag.
- Unpinned ingredients are **skipped by basket automation and flagged for
  manual adding**. Never guessed at silently.
- The staple flag is how store-cupboard items stay off the weekly list. This
  retires the "pantry staples" fog entirely.

What remains open here is the *naming and file shape*: how a canonical name is
spelled and enforced so several Recipes aggregate to one line, how incompatible
units add up (150g cherry tomatoes plus "1 punnet"), and whether the catalogue
is one file per ingredient or a single table.

## Answer

**A single Pin catalogue file, where each Pin declares the one unit its
ingredient must be written in.** Path decided in
[Where Everything Lives](05-where-everything-lives.md).

### The Pin

```yaml
cannellini-beans:
  display: Cannellini beans
  store: waitrose
  unit: can                        # the unit every recipe MUST use
  pack: { qty: 400, unit: g }      # what one purchasable item is; optional
  search_term: Napolina Cannellini Beans
  line_number: 584333
  alternates: [haricot beans]
  staple: false

chicken-breast:
  display: Chicken breasts
  store: soutars
  unit: each
  each_g: 160                      # bridges count <-> mass; corpus says 150-170g
  staple: false
```

Three name fields, each earning its place: the **key** is what recipes cite,
`display` is what you read on a list, `search_term` is what Waitrose actually
needs — and the research proved those last two diverge badly (`Fage 2%` finds
bathroom tissue; `Fage Total 2` finds the product).

### Settled

- **Single file, not one per ingredient.** A catalogue is a lookup table and
  gets read as one. Recipes get their own files because you read a recipe;
  nobody reads a Pin. Roughly 60-100 rows.
- **The Pin declares the unit; recipes comply, and this is checked.**
  Aggregation collapses to addition instead of unit algebra. A recipe using a
  unit that disagrees with its Pin is an **error surfaced at list time**, not a
  silent miscount. `each_g` bridges count and mass where a real recipe needs
  both.
- **Shopping lists quantify in Pin units** — `Cherry tomatoes, 300g`,
  `Cannellini beans, 4 cans` — exactly as the original CSV already did. `pack`
  identifies the product but never distorts the quantity, so a Pin missing
  `pack` still produces a usable list.
- **One ingredient per line. No `or`.** Substitution lives on `alternates`,
  which is a shelf problem, not a cooking one.
- **Store routing lives on the Pin.** Stable: eggs and meat from Soutars, fish
  from Dorset Meats, the rest Waitrose.
- **`staple: true` filters an ingredient out of the shopping list** while
  keeping it in the recipe. Confirmed members: salt, pepper, all oils
  including truffle.

### The cost, and where it lands

The corpus is **not** unit-consistent today, so extraction has to normalise it:

| Ingredient | Currently written as |
| --- | --- |
| Cannellini beans | `1 can`, `150g`, `240g`, `300g` |
| Chicken breast | `2 chicken breasts`, `300g chicken breast, diced` |
| Pre-cooked lentils | `1 pack`, `250g` |

Plus one `150g cannellini **or haricot** beans` to split. This work belongs to
[Extract The Corpus](07-extract-the-corpus.md).
