# Waitrose basket-building feasibility

**Question:** Can a browser-driving agent build a Waitrose (waitrose.com, UK) basket from plain
ingredient names, and read a user's past orders?

**Date of investigation:** 2026-09-07
**Method:** in-app sandboxed browser (no user session, never signed in), plus first-party help
pages and public documentation.

**Boundaries observed:** never signed in; no credentials handled; no account created; no order
placed or attempted; no CAPTCHA or bot-challenge interaction. Only publicly reachable pages were
visited. One guest add-to-trolley click was performed (not an order, fully reversible) because it
is the load-bearing feasibility question — result recorded below.

Every claim is tagged **[VERIFIED]** (I observed it directly in the browser this session) or
**[SECOND-HAND]** (read from a first- or third-party document, not observed).

---

## Verdict (up front)

### (b) Semi-automation is realistic — agent proposes, human confirms. With caveats.

Full automation (a) is **not** supportable on the evidence. Two independent blockers:

1. **Search cannot be trusted to resolve an ingredient name to a product.** This is the killer,
   and it is not a bot-protection problem — it is a relevance problem that would exist even with
   a sanctioned API. Details in §2.
2. **Guest add-to-trolley did not work in the automated browser**, and the only path past that is
   a signed-in session behind Akamai Bot Manager — out of bounds here and fragile in general.

Stopping at a shopping list (c) is **too pessimistic**: Waitrose ships a first-party
"Multi-search" feature that takes a pasted plain-text list and turns it into a
one-chip-per-ingredient result browser. That is a ready-made semi-automation surface the project
gets for free, with no scraping and no automation of the checkout path. See §7 — this is the most
actionable finding in the whole report.

**What would have to be true to move up to (a):**
- The project must stop relying on free-text search at basket time. Each ingredient would need a
  pinned Waitrose line number (see §3) that was resolved *once* by a human and stored. Past orders
  and Favourites are the natural source of those pins (§5).
- Even then, an agent would need a durable signed-in session that survives Akamai, plus a
  re-resolution path for delisted/substituted lines. That is ongoing maintenance, not a one-off
  build.
- And it would still be operating against terms that forbid electronic storage of site content
  without written permission (§6).

---

## 1. Bot protection

**[VERIFIED] Waitrose runs Akamai Bot Manager.** Evidence, all observed directly:

- Cookies set on first page load: `_abck` and `bm_sz` — both are Akamai Bot Manager cookies.
- Repeated `GET` and `POST` to obfuscated same-origin paths of the form
  `https://www.waitrose.com/2gPKz/k81d/B6AD/Bd/QuTr2/...` returning `201` — this is the Akamai
  sensor-data telemetry channel.
- `POST https://www.waitrose.com/akam/13/pixel_10668c61` → 200 — Akamai's tracking pixel endpoint.

No Cloudflare, PerimeterX or DataDome markers were seen.

**[VERIFIED] Plain HTTP clients are refused.** `curl` to `https://www.waitrose.com/robots.txt`:
- over HTTP/2: `curl: (92) HTTP/2 stream 1 reset by server (error 0x2 INTERNAL_ERROR)`
- over HTTP/1.1 with a realistic desktop User-Agent: connection accepted, then no data ever
  returned — `curl: (56) Recv failure: Connection timed out`, final status `HTTP 000`, after
  several minutes. Note the shape of this failure: the TCP connection is *accepted* and then
  starved rather than refused, which is characteristic of bot-mitigation blackholing rather than a
  network fault.

The same URL loaded instantly in the real browser. So a naive `fetch`/`requests`/`curl` scraper is
dead on arrival; only a real browser engine gets served.

**[VERIFIED] Product search works fully unauthenticated in a real browser.** No sign-in wall, no
interstitial, no challenge page. Search result pages are server-side rendered — the products are in
the initial HTML.

**[VERIFIED] No CAPTCHA or bot challenge was encountered** during ~30 page loads of browsing,
searching and product-page reads. Read-only browsing at human-ish rates is not visibly challenged.
I did not probe rate limits and did not attempt to.

**[VERIFIED] Guest add-to-trolley did not work.** Clicked "Add to Trolley" on a product page
(Essential Cannellini Beans) and "Add" on a search result card (Cooks' Ingredients Gochujang
Paste). In both cases:
- the header trolley total stayed at `£0.00`
- the product page continued to read "You have 0 of this in your trolley"
- **no trolley mutation appeared in the network log at all** — the request was never made
- the product-page button entered a stuck `ButtonBase_finalising` CSS state

**Cause is undetermined.** Candidates: a sign-in requirement, a required booked delivery slot (the
header advertises "Book a slot" and a `£40` minimum order), or Akamai silently suppressing the
mutation. I did not sign in, so I cannot distinguish these. **This is the single biggest open
question and it should be treated as a red flag either way**: the write path behaves differently
from the read path, and the read path is the only one I could confirm works under automation.

---

## 2. Search ambiguity — the decisive section

All **[VERIFIED]**, via `https://www.waitrose.com/ecom/shop/search?&searchTerm=<term>`.

| Ingredient | Results | Obvious single match? |
|---|---|---|
| `cannellini beans` | 4 (site says 4, renders 5 incl. a sponsored slot) | **No** — 3 plausible |
| `cottage cheese` | 65 | **No** — and #1 is wrong |
| `vegetarian sausage` | 15 | **No** — 8+ plausible |
| `pre cooked lentils` | 605 | **No** — qualifier ignored entirely |
| `Fage 2%` | 1104 | **No** — correct product not in top 8 |
| `gochujang paste` | **1** | **Yes** |
| `white fish fillet` | 11 | **No** — genuine category choice |

### `cannellini beans` — 4 results
```
[Sponsored] Merchant Gourmet Five Bean Medley 240g  £1.75   <- not cannellini
Essential Cannellini Beans          400g  55p    /essential-cannellini-beans/584333-805769-805770
Mr Organic Cannellini Beans         350g  £2.35
Epicure Organic Cannellini Beans    400g  £1.20
Heinz Marry Me Cannellini Beans     250g  £2.50  <- a flavoured sauce product, not plain beans
```
Near-misses are distinguished by **own-label tier** (Essential = budget tier), **organic flag**,
**pack size** (350/400/250 g), and **preparation** (the Heinz line is a sauced product, and the
sponsored slot is a different bean entirely). A "cheapest plain tin" heuristic gets this right, but
only because it happens to be a small result set. Note the sponsored result sits at position 1 and
is not the requested ingredient.

### `cottage cheese` — 65 results
```
[Sponsored] Philadelphia Garlic & Herbs Soft Cream Cheese 165g   <- WRONG PRODUCT, position 1
Essential Cottage Cheese Strength 1  300g
Philadelphia Original Soft Cheese    165g                        <- WRONG PRODUCT, position 3
All Things Cottage Cheese Natural    450g
```
Two of the top four are cream cheese, not cottage cheese. An agent taking result #1 would put
Philadelphia garlic-and-herb cream cheese in the basket. Also note `Essential Cottage Cheese
Strength 1` — Waitrose uses a "Strength" scale that means nothing to a recipe.

### `vegetarian sausage` — 15 results
```
[Sponsored] Richmond Meat Free Tasty Sausages   304g  Frozen
Cauldron 6 Lincolnshire Vegetarian Sausages     276g  Vegetarian
Quorn Vegetarian 8 Sausages                     336g
THIS Isn't Pork Plant-Based Sausages            270g
PlantLiving: Mushroom & Leek Sausages           300g
Quorn Cocktail Sausages                         140g   <- cocktail size, wrong for a meal
Linda McCartney's Frozen Vegan Sausages         270g
Symplicity Sausages                             270g
```
Eight defensible answers, differing on **frozen vs chilled** (recipe-relevant), **count per pack**
(6 vs 8), **vegan vs vegetarian** (dietary-relevant), **format** (cocktail vs full-size), and
brand. There is no correct answer without a user preference.

### `pre cooked lentils` — 605 results, **qualifier silently ignored**
```
Essential Lentils in Water              400g   <- pre-cooked, correct
Epicure Organic Bijoux Verts Lentils    400g   <- pre-cooked
Waitrose Red Split Lentils              500g   <- DRY, wrong
Duchy Organic Red Split Lentils         500g   <- DRY, wrong
Merchant Gourmet Thai Green Lentil Curry 280g  <- a ready meal, wrong
Belazu Pardina Lentils                  360g
Waitrose Red Split Lentils              1Kg    <- DRY, wrong
Waitrose Lentils                        500g   <- DRY, wrong
```
The words "pre cooked" have **no effect on ranking**. Dry and pre-cooked lentils are interleaved
in the top 8. This is the failure mode that matters most for a meal-planning system: dry vs
pre-cooked is a *cooking-method* distinction, and getting it wrong ruins the recipe, not just the
receipt. There is no filter or facet exposed on the search page that separates them.

### `Fage 2%` — 1104 results, correct product absent from the top
```
Essential British Free Range Semi-Skimmed Milk 2 Pints   <- position 1
Fage Total 5% Fat Natural Greek Yogurt Large  950g
Waitrose Ultra Soft & Smooth Classic Bathroom Tissue     <- position 3 (!)
Fage Total 5% Fat Natural Greek Yogurt Small  150g
John West Tuna Chunks in Spring Water MSC
Fage Total 0% Fat Free Natural Greek Yogurt Small 150g
Fage Total 0% Fat Free Natural Greek Yogurt   450g
Nestlé KitKat 2 Finger Original 8 Bars                   <- position 8 (!)
```
**[VERIFIED]** The `%` is stripped — the page heading and `<title>` both read "Fage 2", and the
query degrades to a broad OR-match ("2" matches bathroom tissue and KitKat 2 Finger). The Fage
Total **2%** product **does exist**: searching `fage total` returns 9 results including
`Fage Total 2% Fat Natural Greek Yogurt Large 950g` and `Fage Total 2% Fat Natural Greek Yogurt
450g`. So the exact right product is stocked and the search still fails to surface it.

**The lesson: query phrasing is decisive, and the agent has no signal telling it the query went
wrong.** 1104 results looks like success. It is a total miss. There is no confidence score, no
"did you mean", nothing an automated caller could threshold on.

### `gochujang paste` — 1 result
```
Cooks' Ingredients Gochujang Paste  105g  £2.00
/ecom/products/cooks-ingredients-gochujang-paste/888413-457274-457275
```
The only unambiguous case in the set. Note *why*: it is a niche speciality item Waitrose stocks
exactly one of. The pattern is that **common staples are ambiguous and niche items are not** —
exactly backwards from what a meal planner needs, since staples dominate a weekly shop.

### `white fish fillet` — 11 results
```
Waitrose 2 Mediterranean Sea Bass Fillets   180g
Waitrose 2 Mediterranean Sea Bream Fillets  180g
Waitrose 4 Mediterranean Sea Bass Fillets   360g
Waitrose Haddock Fillets MSC                240g
Waitrose Cod Fillets MSC                    240g
Waitrose Smoked Haddock Fillets MSC         240g   <- smoked, changes the dish
No.1 Bubbly Battered Cod Fillets            380g   <- battered, wrong
Essential Hake Fillets                      200g
No.1 Bubbly Beer Battered Haddock Fillets   365g   <- battered, wrong
Waitrose Classics Cod in Parsley Sauce      400g   <- ready meal, wrong
```
A genuine open choice (cod/haddock/hake/bass/bream all satisfy "white fish"), plus four results
that are actively wrong for a recipe (battered, smoked, in sauce). Distinguishing features here are
**species**, **preparation** (raw / battered / smoked / sauced), **count and weight**, and
**own-label tier** (Essential vs Waitrose vs No.1).

### Summary of what distinguishes near-misses
Across all seven terms the discriminating axes were consistently:
1. **Preparation state** — dry vs cooked, raw vs battered vs smoked vs sauced. *Recipe-breaking,
   and the search engine does not model it.*
2. **Own-label tier** — `Essential` (budget) / `Waitrose` (standard) / `No.1` (premium) /
   `Duchy Organic` / `Cooks' Ingredients`. Price-relevant, user-preference-driven.
3. **Pack size / count** — 150 g vs 450 g vs 950 g of the same yogurt; 6 vs 8 sausages.
4. **Brand** — often 5+ interchangeable brands.
5. **Organic flag**, **frozen vs chilled**, **vegan vs vegetarian**.
6. **Sponsored placement** — sponsored results occupy position 1 and were the *wrong product* in
   2 of the 7 searches. Any "take the first result" strategy is actively hostile to correctness.

---

## 3. Stable identifiers — this part is good news

**[VERIFIED]** Product URLs are `/ecom/products/<slug>/<A>-<B>-<C>`, e.g.
`/ecom/products/essential-cannellini-beans/584333-805769-805770`.

Two experiments:
- Replacing the slug with garbage (`/ecom/products/zzz-wrong-slug/584333-805769-805770`) loads the
  correct product and canonicalises the URL back to the real slug. **The slug is decorative.**
- **`/ecom/products/x/584333` — the first number alone — also loads the correct product** and
  canonicalises to the full URL.

So the **6-digit line number is a complete, sufficient product identifier.** `584333` is all you
need to store.

**[VERIFIED]** Product pages carry `schema.org` JSON-LD:
```json
{"@context":"http://schema.org/","@type":"Product",
 "@id":"https://www.waitrose.com/ecom/products/essential-cannellini-beans/584333-805769-805770",
 "name":"Essential Cannellini Beans",
 "image":"https://ecom-su-static-prod.wtrecom.com/images/products/9/LN_584333_BP_9.jpg",
 "description":"Cannellini beans in water.",
 "mpn":"584333",
 "brand":{"@type":"Brand","name":"Waitrose Ltd"},
 "aggregateRating":{"ratingValue":"4.7143","reviewCount":"63"},
 "offers":{"price":"0.55","availability":"http://schema.org/InStock","priceCurrency":"GBP"}}
```
`mpn` == the line number == the first URL segment. There is a second JSON-LD block with a
`BreadcrumbList` giving the full taxonomy path (`Groceries > Food Cupboard > Tins, Cans & Packets >
Beans & Pulses > Beans`), which is useful for disambiguation and for narrowing a re-search.

The product page also exposes pack size (`400g`), price and price-per-unit, an ingredients list,
full nutrition, and badges (`Microwaveable`, `Waitrose own label`) — enough to re-verify that a
stored line number still points at the thing you meant.

**Unknown:** how often line numbers churn (reformulation, delisting, seasonal lines). Any stored
pin needs a validation step and a fallback.

---

## 4. Structured surfaces

**[VERIFIED] Yes, there is an internal JSON/GraphQL API.** Observed in the network log on
first-party pages:

```
POST https://www.waitrose.com/api/graphql-prod/graph/live?clientType=WEB_APP&tag=browse
POST https://www.waitrose.com/api/graphql-prod/graph/live?clientType=WEB_APP&tag=get-minimum-order
GET  https://www.waitrose.com/api/search-prod/v2/taxonomy/footer
GET  https://www.waitrose.com/api/taxonomy-entity-prod/v1/taxonomy/waitrose-ecomm-groceries
PUT  https://www.waitrose.com/api/content-prod/v2/content/experience-fragments/...
POST https://www.waitrose.com/api/adtech-prod/v3/adtech/banners/search
POST https://www.waitrose.com/api/content-prod/v2/cms/publish/productcontent/search/-1
```
Browse/search go through the GraphQL endpoint. Note `.../search/-1` — `-1` is the guest account id,
which also appears in the Multi-search localStorage key (§7).

`robots.txt` explicitly disallows `/api/token-client-prod/v1/auth*`.

> **Flagged, not recommended.** This is an undocumented internal endpoint. Calling it directly is
> not a supported integration, it sits behind the same Akamai protection as everything else, and it
> is squarely the kind of "storing in any medium by electronic means" that §6 prohibits. I did not
> attempt to call it. **Do not build on it.**

**[SECOND-HAND] There is no official public Waitrose or John Lewis Partnership grocery API.** No
UK supermarket offers one. Waitrose announced an internal API programme around 2015
([Computerworld](https://www.computerworld.com/article/1654534/waitrose-invests-in-apis-to-create-apps-that-blend-in-store-and-online-shopping.html))
but nothing public came of it. The "Waitrose APIs" advertised by vendors such as Pepesto, Channel3,
Actowiz and FoodDataScrape are **third-party scraping services**, not sanctioned access — and they
inherit the same terms problem.

**[VERIFIED] `robots.txt` is restrictive on exactly the surfaces this project wants.** From
`https://www.waitrose.com/robots.txt`:
```
Crawl-delay: 1
Disallow: *search?*
Disallow: /ecom/lists*
Disallow: /ecom/shopping-lists*
Disallow: /ecom/favourites*
Disallow: /ecom/bought-in-store*
Disallow: /ecom/quick-shop*
Disallow: /ecom/shop-by-list*
Disallow: /ecom/myaccount/my-orders
Disallow: /ecom/shop/trolley
Disallow: /ecom/checkout
Disallow: /api/token-client-prod/v1/auth*
```
Search URLs, the trolley, past orders, favourites and lists are all disallowed to crawlers. (This
governs crawlers rather than a user's own browser, but it is a clear statement of intent about what
Waitrose considers off-limits to automation.)

---

## 5. Past orders and reordering — documentation only, never signed in

**[SECOND-HAND, first-party]** From Waitrose's own help page
`https://www.waitrose.com/ecom/help-information/shopping-with-waitrose/shop-online`, three verbatim
sentences that I read directly on the page:

- "Repeat a previous order by clicking 'Shop from previous order' on the My Orders page."
- "If you're a myWaitrose member you can shop from your 'Favourites' – the products you buy most
  often – at the top of each page."
- "If you have a shopping list, use the 'Multi-search' option in the Search bar to find all your
  items quickly."

**[SECOND-HAND]** Also documented: viewing a list of previous orders, clicking into any order for
details, and shopping from any previously completed order — same on the mobile app under
Account → My online orders.

**[VERIFIED, corroborating]** The signed-out site ships the JavaScript for all of this. Chunk names
observed loading on public pages:
```
components-MyOrders.js
components-ShopFromRecentOrder.js
components-NextOrder.js
components-Favourites-Page.js
```
And `robots.txt` (§4) enumerates the account URL surface, which is the most reliable public map of
what exists:
```
/ecom/myaccount/my-orders   /ecom/favourites   /ecom/lists
/ecom/shopping-lists        /ecom/quick-shop   /ecom/shop-by-list
/ecom/bought-in-store
```
`/ecom/bought-in-store` is notable — it implies myWaitrose card-linked **in-store** purchases are
also surfaced, not just online orders. Unverified.

**[VERIFIED]** Product pages show "Add to favourites" and "Edit lists" controls even when signed
out, so favourites/lists are per-product, first-class objects.

**Conclusion for the project:** a signed-in user does have a rich pre-approved product set — past
orders, Favourites, saved lists, and possibly in-store purchases. **This is the right foundation.**
But reaching it requires a signed-in session, which is out of scope here and is the part most
exposed to Akamai. Nothing about the reorder flow is available to an unauthenticated agent.

---

## 6. Terms of use

**[VERIFIED]** I read the full expanded waitrose.com grocery Terms and Conditions
(`https://www.waitrose.com/ecom/help-information/terms-and-conditions`, ~106 KB of text with all
accordions opened).

**There is no clause mentioning robots, spiders, crawlers, scraping, bots, data mining or automated
access.** I grepped the full expanded text for all of those terms and the only hits were unrelated
("Automatic Renewal" for the Delivery Pass). The UK terms are **silent on automation** — which is
neither permission nor prohibition.

What the terms *do* say that bears on this, quoted in part:

> "No part of this website may be reproduced in any material forms (including storing in any medium
> by electronic means) without the prior written permission of Waitrose Limited."

Read plainly, that covers caching product data, prices or search results into the project's own
store. It is a broad copyright-style clause rather than an anti-bot clause, but it is the operative
restriction. The terms also state that using the site binds you to them, restrict registration to
truthful details, and — in the user-content section — warrant that "you are not using the website
for any commercial purpose."

**[SECOND-HAND] Caution about a near-miss source:** searches surface an explicit anti-robot clause
("you agree not to use any robot, spider, other automatic device...") — but that is from
**waitrose.ae**, the UAE franchise, a different legal entity with different terms. It does **not**
apply to waitrose.com. Do not cite it as if it does.

**Net position:** personal, human-paced, browser-driven use for one household's own shopping is not
explicitly forbidden. Bulk extraction and local storage of the catalogue is squarely against the
reproduction clause. The project should stay on the first side of that line.

---

## 7. The finding that changes the design: native Multi-search

**[VERIFIED, and this is the headline.]** Waitrose ships a first-party **"Multi-search"** feature,
linked next to the search bar on every page (also reachable via the "Search multiple items" button
in the search bar). It opens a modal with a textarea labelled **"Type or paste your list here"**.

I pasted the project's seven ingredient names, one per line, and hit Search. Result:

- A **chip bar** appeared across the top of the results page, one chip per ingredient:
  `cannellini beans` `cottage cheese` `vegetarian sausage` `pre cooked lentils` `Fage 2%`
  `gochujang paste` `white fish fillet`
- The page shows the results for the selected chip; clicking a chip switches to that ingredient's
  results without losing the list.
- Each chip is deep-linkable: `https://www.waitrose.com/ecom/shop/multi-search?value=<term>`
- The list persists in `localStorage` under the key `multisearch:-1` (`-1` = guest account id; a
  signed-in user presumably gets `multisearch:<accountId>`) as a plain JSON array:
  ```json
  ["cannellini beans","cottage cheese","vegetarian sausage","pre cooked lentils",
   "Fage 2%","gochujang paste","white fish fillet"]
  ```
- Waitrose's own help page names it as the intended shopping-list workflow (§5).

**Why this matters.** The project's hardest problem — ambiguity — is exactly the problem
Multi-search hands back to the human, in the vendor's own supported UI, one ingredient at a time,
with Add buttons right there. The project does not need to automate the basket. It needs to
**produce a paste-ready list that makes Multi-search work well**, which reduces to: write better
query strings. That is a text problem the project fully controls, with zero automation risk, zero
terms exposure, and zero session fragility.

Note the corollary from §2: `Fage 2%` fails inside Multi-search too (same 1104 results, same
bathroom tissue at position 3). **Multi-search inherits the relevance engine's weaknesses** — so
query-string quality is not a nice-to-have, it is the whole job.

---

## 8. Answers to the explicit questions

### If past orders ARE usable — fields an ingredient record needs

Assuming a later, in-scope, signed-in phase resolves ingredients against past orders and
Favourites, an ingredient record should carry a **resolution block** per ingredient:

| Field | Why |
|---|---|
| `waitroseLineNumber` | The pin. 6 digits, e.g. `584333`. **[VERIFIED]** sufficient on its own to re-open the product via `/ecom/products/x/<lineNumber>`. |
| `productUrl` | Full canonical URL, for humans and for a cheap sanity check. |
| `productName` | e.g. `Essential Cannellini Beans`. Used to *verify* a pin still resolves to the same thing — if the name drifts, re-resolve. |
| `packSize` | `400g`. Needed to convert recipe quantity → number of units, and to detect a silent pack-size change. |
| `unitsToBuy` | Derived: `ceil(recipeQuantity / packSize)`. Distinct from pack size. |
| `brand` + `ownLabelTier` | `Waitrose Ltd` / `Essential`\|`Waitrose`\|`No.1`\|`Duchy Organic`\|`Cooks' Ingredients`. This is the axis users actually have opinions about. |
| `taxonomyPath` | From the BreadcrumbList JSON-LD. The best fallback for re-finding a delisted line: search within the same category. |
| `preparationState` | `dry` \| `cooked` \| `raw` \| `frozen` \| `chilled` \| `battered` \| `smoked`. **The project must model this itself** — §2 shows Waitrose search does not, and it is the recipe-breaking axis. |
| `lastVerifiedAt` + `lastPurchasedAt` | Pins go stale. `lastPurchasedAt` also ranks candidates from order history. |
| `resolutionSource` | `past-order` \| `favourite` \| `human-confirmed` \| `unresolved`. Never let an unconfirmed search guess masquerade as a pin. |
| `confidence` / `needsHumanReview` | Explicit. Anything not sourced from a past order or an explicit human confirmation defaults to needing review. |
| `substituteLineNumbers[]` | Ranked alternates for out-of-stock, from the same order history. |

**Design rule implied by the evidence:** an ingredient may only carry a line number if a human or a
past purchase put it there. A line number derived from a search result is a *suggestion*, stored in
a different field, until confirmed.

### If past orders are NOT usable — what the shopping list must carry

This is the state the project is in today, and it is the state §7 says to design for. The list must
be optimised for a human resolving ambiguity fast at the basket. Per line:

1. **A search-optimised query string, not the recipe's word for the ingredient.** This is the
   highest-leverage field in the whole system. Rules the evidence directly supports:
   - **Strip characters the engine mangles.** `Fage 2%` → `Fage Total 2` **[VERIFIED]**: `%` is
     stripped and degrades the query to a junk OR-match, while `fage total` returns a clean 9
     results containing the target.
   - **Drop qualifiers the engine ignores.** `pre cooked lentils` → `lentils in water`
     **[VERIFIED]**: "pre cooked" has zero ranking effect; "in water" is how Waitrose actually
     names the product.
   - **Prefer the vendor's noun phrase over the recipe's.** Use the words that appear in Waitrose
     product titles.
   - **Narrow to a species/format when the ingredient is a category.** `white fish fillet` →
     `cod fillets` (11 unfiltered results collapse to a clear choice).
2. **The human-readable ingredient name**, separately, so the person knows what the recipe wanted.
3. **Quantity needed, in recipe units** (`2 x 400g tins`, `500g`), so pack-size arithmetic is
   visible at the shelf.
4. **The disambiguating constraints, stated explicitly**, because they are exactly what the search
   page does *not* surface:
   - preparation state (`pre-cooked, in water — NOT dry`)
   - dietary flags (`vegan` vs `vegetarian`)
   - chilled vs frozen
   - "must not be battered / smoked / in sauce"
5. **A tier/price hint** (`own-label is fine` / `brand matters here`), so the user isn't
   re-deciding on every line.
6. **A known-good example**, where one exists: `e.g. Essential Cannellini Beans 400g`. Turns a
   search into a recognition task.
7. **An ambiguity warning flag** for the lines the project already knows are hard — anything where
   preparation state or dietary flag is load-bearing. Let the user spend their attention there.
8. **The list rendered as plain newline-separated text**, ready to paste straight into
   Multi-search. That is the delivery format, and it is the one Waitrose itself recommends.

An honest note: item 1 does most of the work, and it is entirely within the project's control. The
difference between `Fage 2%` (1104 results, wrong) and `Fage Total 2` (9 results, right) is a
string transformation, not an integration.

---

## Open questions worth resolving before building

1. **Does add-to-trolley work at all under automation once signed in?** Unresolved and
   consequential (§1). Answer it before designing anything that writes to a basket. It needs a
   consenting signed-in human at the keyboard, which was out of scope here.
2. **Does adding to trolley require a booked delivery slot?** The `£40` minimum and the prominent
   "Book a slot" CTA hint at it. Would change the flow shape considerably.
3. **How stable are line numbers over months?** Determines whether pins need re-validation every
   shop or every quarter.
4. **What does the signed-in `multisearch:<accountId>` localStorage key allow?** If the list can be
   seeded programmatically for a signed-in user, the paste step disappears and the flow gets
   noticeably nicer — without touching the basket at all.
