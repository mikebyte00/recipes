# Can Claude Drive Waitrose

Type: research
Status: resolved
Blocked by: —

## Question

Can an agent actually build a Waitrose basket, and can it read past orders?

Establish, against the live site:

1. Whether sign-in is drivable, or whether it blocks automation (CAPTCHA, bot
   detection, SMS/2FA).
2. Whether past orders are retrievable, and what a past-order record exposes —
   product name, size, price, a stable product ID, a reorder affordance.
3. Whether search-then-add-to-basket works, and how ambiguous a search for a
   plain ingredient name like "cannellini beans" turns out to be.
4. Whether there is any structured surface (an API the site itself calls, a
   reorder endpoint) that beats screen-driving.

**This ticket does not place an order and does not enter credentials.** It
establishes feasibility and reports what the mapping between an ingredient and
a purchasable product would have to look like.

The answer gates [How Ingredients Are Named](04-how-ingredients-are-named.md):
if past orders give stable product IDs, ingredient records can point at them
directly and the whole matching problem mostly evaporates. If not, the shopping
list has to carry enough description for a human to resolve ambiguity.

## Answer

**Original verdict: semi-automation only. Do not build basket automation.**
**Superseded in part, 14 September 2026 — see [Reassessment](#reassessment-14-september-2026).**

Full report: [waitrose-feasibility.md](../research/waitrose-feasibility.md).
Verified first-hand in a sandboxed browser, never signed in, no order touched.

**The blocker is search relevance, not bot protection.** Only 1 of 7 real
ingredient names resolved unambiguously:

- `Fage 2%` → **1104 results**; the `%` is stripped, position 1 is semi-skimmed
  milk, position 3 is bathroom tissue. The product is stocked — `fage total`
  returns a clean 9 — so search misses a stocked item **with no signal that
  anything went wrong**. Silent wrongness is the failure mode that matters.
- `pre cooked lentils` → 605 results, the qualifier ignored entirely; dry and
  pre-cooked interleaved. Recipe-breaking.
- `cottage cheese` → 65 results, positions 1 and 3 are *cream* cheese.
- Sponsored results sit at position 1 and were wrong in 2 of 7 searches.

This would break identically behind a sanctioned API, so no amount of access
fixes it.

**The finding that redesigns the feature: Waitrose ships a first-party
Multi-search.** Paste a newline-separated list, get one chip per ingredient with
per-ingredient results and Add buttons. Deep-links as
`/ecom/shop/multi-search?value=<term>`. Waitrose's own help page recommends it
for shopping lists. **The project gets its semi-automation surface for free** —
no scraping, no basket driving.

**Supporting facts:**

- Akamai Bot Manager confirmed. A real browser is served fine (no CAPTCHA in
  ~30 loads); every non-browser HTTP client is dead — `curl` is accepted then
  starved, presenting as a **hang, not an error**.
- Add-to-trolley **silently failed as a guest**: trolley stayed £0.00 and no
  network request was made at all. Cause undetermined.
- **Stable IDs are genuinely good.** The 6-digit line number alone resolves —
  `/ecom/products/x/584333` works, the slug is decorative. JSON-LD exposes
  `mpn`, name, price, taxonomy. A Pin has something solid to hold.
- `robots.txt` **disallows exactly the surfaces of interest**: `*search?*`,
  `/ecom/favourites*`, `/ecom/myaccount/my-orders`, `/ecom/shop/trolley`,
  `/ecom/lists*`. Multi-search deep links are a human-facing navigation the
  user clicks, which is a different act from crawling those paths.
- UK terms are **silent on scraping**; the live clause is copyright-shaped.
  The anti-robot clause search engines surface belongs to **waitrose.ae**, a
  different entity — do not cite it.
- An internal GraphQL endpoint exists. Flagged, **not** recommended.
- Past orders: "Shop from previous order", Favourites and saved lists all
  exist, all behind sign-in, all `Disallow`ed in `robots.txt`.

**Consequence for the design.** The leverage moves to a place the project fully
controls: the gap between `Fage 2%` (1104 results, wrong) and `Fage Total 2`
(9 results, right) is a **string transformation**. That is the thing worth
building.

## Reassessment, 14 September 2026

**Basket automation is built, by line number.** `Orders/BASKET.md` holds the
procedure. The original verdict stands for everything it actually measured; it
answered a different question from the one that got asked.

**The blocker never applied to this design.** The verdict rested on search
relevance — 1 ingredient in 7 resolving. Filling a basket from a Plan's Waitrose
table **never searches**. Every row already carries a confirmed line number, and
this ticket's own finding is that the 6-digit number resolves on its own. The
matching problem the verdict was about had already been solved by `PINS.md`,
which did not exist when the research ran.

**"Add-to-trolley silently failed as a guest, cause undetermined" is resolved:
the cause was being a guest.** Verified first-hand in the user's signed-in
session — quantity 5 of line 097155 added on one click, reconciled exactly
against the trolley total. The failure is specific to guest sessions, and it
still presents as silence, which is why `BASKET.md` opens by checking sign-in.

**Three findings that only appear when you write, not read:**

- **Quantity is a typeable text box**, not a stepper. One type, one click, any
  quantity. This is what makes the whole thing cheap.
- **Setting that box programmatically silently does nothing** — the page's own
  state stays at 1 and the click adds nothing, with no error. Real events only.
- **The header trolley total is stale after an add** and shows neither the old
  nor the new value. Verification reads the trolley page.

**The robots.txt line was crossed deliberately.** `/ecom/shop/trolley` is
`Disallow`ed. The user overruled it on the reasoning already used for the
harvest — their own session, their own basket, at their own request, not a
crawler — and asked for the decision to be recorded rather than re-litigated.
It extends to the trolley and product pages and **nothing further**; placing an
order stays the user's, and credentials are never entered.

**Unchanged:** Multi-search remains the surface for Unpinned items, which have
no line number by definition. This automates the pinned lines, not the list.
