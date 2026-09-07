# Harvesting Past Orders

Type: grilling
Status: open
Blocked by: 01, 04

## Question

How does past-order history become Pins, on an ongoing basis?

This is not a one-off seeding job. It is the loop that makes the system improve
by itself:

> An Unpinned ingredient is added to the basket by hand → it appears in order
> history → the next harvest turns it into a Pin → the following week it is
> automated.

The manual work the system could not avoid is exactly what feeds it. The
Unpinned list shrinks without anyone doing a dedicated pinning chore.

Grill on:

- **When does a harvest run?** On demand, as a step in weekly planning, or as
  its own skill invoked occasionally?
- **How does a harvested product find its canonical ingredient?** "Essential
  Cannellini Beans 400g" has to become `cannellini-beans`. That match is the
  hard part, and getting it wrong writes a bad Pin that then looks settled.
- **What happens on conflict** — history shows three different cottage cheeses
  bought across six orders. Most recent wins, most frequent wins, or ask?
- **Does a harvest ever overwrite an existing Pin,** or only fill gaps? Silent
  overwrites would undo deliberate choices.
- **How is a harvest reviewed** before its Pins are trusted?

Open fact needed from the user: how many past orders are reachable, and how far
back. A short window means seeding covers less of the pool and the first
harvest is smaller than hoped.

## What the research found

[Can Claude Drive Waitrose](01-can-claude-drive-waitrose.md) resolved, and it
complicates this ticket without killing it.

Past orders **do** exist as a rich pre-approved set — "Shop from previous
order", Favourites, saved lists. But all of it sits **behind sign-in**, and
`robots.txt` explicitly disallows `/ecom/myaccount/my-orders`, `/ecom/lists*`
and `/ecom/favourites*`.

So automated harvesting is off the table as originally imagined. What remains
open is whether a **user-driven** path works: the user is signed in and looking
at their own order history, and exports or copies it themselves, with the
project parsing what they hand over. That respects both the sign-in boundary
and `robots.txt`, because the user is reading their own data through the normal
interface.

Grill on whether that manual export is cheap enough to be worth it, or whether
Pins are better built up incrementally from the weekly Unpinned list alone —
which needs no order history at all, just patience.

## Comments

**The order-history reach question is answered.** It had been asked three times
and is the fact this ticket said it was waiting on. Captured at `Orders/` in
the repo root, pulled from Waitrose "My Orders" on 07 September 2026.

### What is reachable

**9 orders, back to 25 January 2026** — roughly seven and a half months. Seven
completed, two cancelled. **Three carry full line-item detail** (11, 25 and
31 August); the other six are summary rows only (date, status, total).

Per line item the capture holds **product name, pack size, quantity, cost**,
grouped under Waitrose's own section headings (Food Cupboard, Fresh & Chilled,
Frozen, Bakery, Household, Toiletries). **95 distinct products** across the
three detailed orders.

That is enough to mint Pins with a name, a pack size and a real purchase
history. It is not enough for two things:

### Gap 1 — no product line numbers

The files carry **order** numbers (e.g. 1000000003) but no **product** line
numbers. [Can Claude Drive Waitrose](01-can-claude-drive-waitrose.md) found
line numbers to be the stable, reliable identifier, and the eventual route by
which the basket question could be revisited at all. Pins minted from this
capture are name-and-size only.

**This ticket must decide whether a harvest can capture line numbers**, and if
not, whether Pins carry a hand-added one later. It changes what
[The Query String Generator](10-the-query-string-generator.md) can lean on.

### Gap 2 — Waitrose only, by definition

No chicken, eggs, steak, salmon, bream or bass appear anywhere — correctly, as
those come from Soutars and Dorset Meats, which have no online order history.
The only fish present is the fakeaway's frozen lemon sole.

**So the protein Pins cannot come from a harvest at all** and must be authored
by hand. Roughly seven Pins, but they cover every dinner in the corpus.

### The finding worth more than the mechanism

The capture is direct evidence for why a Pin has to exist: **the word a Recipe
uses is routinely not the word the product uses.**

| Recipe says | What was actually bought |
|---|---|
| parmesan | Duchy Organic **Parmigiano Reggiano** DOP |
| spring onions | Duchy Organic **Salad Onions** Bunch |
| pine nuts | Waitrose Duchy Organic **Pine Kernels** |
| light cream cheese | Duchy Organic **Soft Cheese** Strength 1 |
| oat milk | MOMA Organic **Oat Barista** |
| cherry tomatoes | Duchy Organic **Cherry Vine** Tomatoes |
| pre-cooked Puy lentils | Epicure Organic **Bijoux Verts** Lentils |

Searching Waitrose for the recipe's word finds none of these. This corroborates
that ticket's "1 of 7 ingredients resolved cleanly" from an entirely
independent direction, and it is the concrete argument for harvesting rather
than generating.

### Two cautions for whoever builds the harvest

- **An order is the household shop, not the meal plan.** The captures include
  toilet roll, washing liquid, iron supplements, bananas, kiwi, grapes and a
  rye boule. A harvest must filter to food, and then to food a Recipe uses —
  it cannot assume every line is Pin-worthy.
- **Quantities carry pack-size signal worth keeping**: cannellini beans x5,
  smoked tofu x3, chickpeas x3, Fage 2% x3 at 950g. That is the evidence for
  what a Pin's pack size should be.

### Also noted

- `Orders/31-august.md` is **misnamed** — it holds the whole order-history
  index plus the 31 August detail, not just that order. It will mislead a
  future session looking for the history.
- Fresh garlic has never been bought (only Garlic Granules and Garlic
  Mayonnaise), yet recipes call for "1 clove garlic, minced". Honey likewise
  appears only inside "Hot Honey Gochujang" — real honey is a Soutars item.
  Both are Unpinned-by-evidence, exactly the case
  [How Ingredients Are Named](04-how-ingredients-are-named.md) says to flag
  rather than guess.

---

**Update — 07 September 2026: the capture mechanism is built and has run.**

The "whether a user-driven path works" question is **answered by execution**,
not by grilling. Procedure at [`Orders/HARVEST.md`](../../../Orders/HARVEST.md),
run by a browser agent in the user's own signed-in Chrome session, read-only
throughout.

### Result

**113 items across the three August orders, every one carrying a line number,
zero left Unpinned.** 86 distinct products. No completed orders exist after
31 August, so the August scope is complete.

The run also split the misnamed `31-august.md` into `Orders/history.md` (the
order index, with capture status per order) plus a clean `31-august.md`, and
backfilled a `Line` column into all three order files.

### Verification

The agent spot-checked 5 line numbers per order (15 total) against
`/ecom/products/x/<number>`. Independently checked afterwards across the whole
capture:

- All 113 line values are well-formed 6-digit numbers.
- **No product carries two different numbers** across orders, and **no number
  carries two different products.** Repeated buys (cannellini, chickpeas,
  smoked tofu, Fage) resolved identically every time — a sloppy join would have
  produced collisions here and did not.
- All 80 previously-recorded food product names survive **verbatim**; nothing
  was silently tidied, which was the failure mode most likely to destroy the
  naming evidence.

### What this settles, and what it does not

**Settled:** a harvest is cheap — one agent run, minutes, no manual export.
That retires the ticket's "or is incremental Unpinned-only accumulation better"
fork: harvesting won on cost. The reachability question is also closed —
9 orders visible back to 25 January 2026, 7 completed, and everything from
1 August is captured.

**Still open, and still this ticket's to answer:**

- **Canonical-ingredient matching.** `Epicure Organic Cannellini Beans 400g` to
  `cannellini-beans` is untouched. The harvest captured products; it minted no
  Pins. This is the hard part and it is entirely ahead.
- **Conflict resolution.** Now concrete rather than hypothetical: the capture
  holds **two different cottage cheeses** (`Essential Cottage Cheese Strength 1`
  300g and `Longley Farm Yorkshire Natural Cottage Cheese` 250g) and **two
  white chocolates** (`Cooks' Ingredients` 180g and `Green & Black's Organic
  30%` 90g). Recipes call for one of each. Most recent, most frequent, or ask?
- **Overwrite policy** and **review before trust** — untouched.
- **Cadence.** The run showed a no-op harvest costs almost nothing (read the
  index, see nothing new, stop), which makes a weekly-planning step viable in a
  way it might not have been.
- **Churn.** Still unmeasured. Every number here is fresh, so nothing has
  decayed yet — the question surfaces later, and the fix is revalidation the
  harvest can perform against product pages it is already allowed to open.

### Gap in the map surfaced by this run

**No ticket owns minting the Pin catalogue itself.** This ticket owns the
harvest loop; [How Ingredients Are Named](04-how-ingredients-are-named.md)
settled what a Pin *is*; [Extract The Corpus](07-extract-the-corpus.md) owns
recipes. Turning 86 harvested products plus ~7 hand-authored protein Pins into
the actual catalogue sits between them, unassigned.
