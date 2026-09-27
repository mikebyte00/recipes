# Harvesting Waitrose orders

**ALWAYS** prefer to use Claude Chrome extention to control a real browser. Avoid using in-built browser

How to turn a completed Waitrose order into **Pins**, with line numbers, and log
that it was done. Reusable: run it whenever new orders have landed.

**The order itself is not kept.** A harvest reads it, writes the Pins it
justifies, adds a row to `Orders/history.md`, and discards it. Waitrose's own
*My Orders* page is the record of what was bought; this repo keeps only the
decisions an order led to. Ruled on 27 September 2026 in
[Browse The Pool](../.scratch/meal-planning-system/issues/24-browse-the-pool.md):
stored orders held personal data in a public repo, and the page view built from
them went unused.

Written for a browser-driving agent (Claude Cowork) working in the user's own
signed-in session. A human can follow it too; the console snippets are the only
part that assumes DevTools.

## What a line number is, and why the harvest exists

Waitrose product URLs are `/ecom/products/<slug>/<A>-<B>-<C>`:

```
https://www.waitrose.com/ecom/products/essential-cannellini-beans/584333-805769-805770
                                                                  ^^^^^^
```

That 6-digit first segment is the **line number** — a complete product
identifier on its own. `/ecom/products/x/584333` resolves to the right product
and canonicalises its own URL. The slug is decorative. It also appears as `mpn`
in the product page's JSON-LD.

The harvest exists because **the word a Recipe uses is not the word the product
uses**. Recipes say parmesan, spring onions, pine nuts, cream cheese, oat milk;
the products are Parmigiano Reggiano, Salad Onions, Pine Kernels, Soft Cheese,
Oat Barista. Searching for the Recipe's word finds none of them. A harvested
line number is a **Pin** that never has to be guessed again.

## Boundaries

This harvest **reads**. It navigates to order pages in a session the user has
already signed in to, reads what is on screen, and writes `PINS.md` and
`Orders/history.md` — nothing else, and never the order itself.

Three hard guardrails, because the surrounding surfaces are live commerce:

- **Stay on `my-orders` and its order-detail pages.** Trolley, checkout,
  favourites and lists are out of bounds.
- **Place no order and change no basket.** If a page offers "add to trolley" or
  "book a slot", it is the wrong page — go back.
- **Reach product pages by line number only** (`/ecom/products/x/<number>`),
  never by search. Waitrose search is `Disallow`ed and was measured resolving
  1 ingredient in 7 correctly.

`robots.txt` disallows `/ecom/myaccount/my-orders` to crawlers. This procedure
is a person reading their own account, at their own request, in their own
browser — not a crawler indexing a site. **That reasoning covers this harvest
and the basket, and nothing else.**

Driving the basket is **no longer parked**: the user extended that same
reasoning to the trolley on 14 September 2026, and the procedure lives in
[BASKET.md](BASKET.md). It writes; this file still only reads. Read
`.scratch/meal-planning-system/issues/01-can-claude-drive-waitrose.md` before
extending either beyond those two surfaces.

## Scope

**Completed orders dated 1 August 2026 or later.** Skip cancelled orders — they
have no items. Ignore anything earlier; it predates the two-week corpus.

## Steps

### 1. Find what is missing

Read `Orders/history.md`: an order with no harvest date still needs one. Then
check **My Orders** for anything newer than its last row. An order needs
harvesting when it is completed, dated 1 August 2026 or later, and has no
harvest date.

### 2. Read the order

Any of these carries what a harvest needs — every product's name, pack size and
**line number**:

- **A saved copy of the order page** (Chrome's *Save page as*, an `.mhtml`
  file). The product links hold the line numbers; parse the HTML part and read
  every `a[href*="/ecom/products/"]`.
- **The live order page**, in the user's signed-in browser. **Scroll to the
  bottom first** — the item list lazy-loads, and un-scrolled products are
  silently absent — then run:

  ```js
  copy([...new Set(
    [...document.querySelectorAll('a[href*="/ecom/products/"]')]
      .map(a => {
        const m = a.href.match(/\/ecom\/products\/[^/]+\/(\d+)/);
        if (!m) return null;
        const name = (a.innerText || a.getAttribute('aria-label') || '')
          .trim().split('\n')[0];
        return m[1] + '\t' + name;
      })
      .filter(Boolean)
  )].join('\n'));
  ```

**Pasted page text is not enough on its own**: it has names and sizes but no
line numbers. A line number that cannot be read from the order is left out of
the Pin, never guessed — a plausible-looking wrong number is the one failure
this design is built to avoid.

Keep the order in the session's scratch space only. **Never write it into the
repo**: order numbers, the collection branch and postcode, collection windows
and a personal-care category all ride along with the items.

### 3. Mint Pins

Steps 6–9 below. The order is the evidence; read it with product names exactly
as Waitrose writes them, because a tidied name destroys the naming evidence the
harvest exists to collect.

### 4. Log it and discard the order

Add or update the order's row in `Orders/history.md` with today's date in the
*Harvested* column — cancelled orders too, with the reason in place of a date,
so a later run knows they were considered. Then delete the scratch copy.

### 5. Verify before reporting done

When the live site is reachable, spot-check **five** of the line numbers you
wrote by opening `/ecom/products/x/<number>` and confirming the product name and
pack size. A line number read from a saved page's own link needs no second
check — the link *is* the product.

## Completion criterion

Every completed order dated 1 August 2026 or later has a harvest date in
`Orders/history.md`, every Pin the order justified is written or explicitly
declined, and no order file exists in the repo.

## Minting Pins from a harvest

A harvest **proposes**; a human **confirms**. Nothing is minted silently. This
half runs on the order read in step 2, and it writes `PINS.md`.

### 6. Walk the slugs, not the products

Matching is **slug-driven**: read every distinct `ingredient:` key from
`Recipes/`, and seek a product for each. Walking the products instead makes you
filter out toilet roll; walking the slugs never considers it.

Each slug ends in one of three states:

- **Proposed** — a product matches. Carry it to step 7.
- **Conflicted** — two or more products match. Carry every candidate.
- **Absent** — nothing matches. Say so; do not stretch a near-match to fill it.

Naive substring matching scores about 43 hits against 69 misses on this corpus,
and roughly ten hits are wrong — `honey` matching *Hot Honey Gochujang*, `water`
matching *Chickpeas in Water*. **The wrong ones score high**, so no confidence
threshold separates them. Substring matching is a first pass that generates
candidates for a human, never a filter that accepts them.

### 7. Put every proposal to the user

Show the slug, the product, its line number and pack size. Group the clean
proposals so they can be confirmed as a block with exceptions named; put each
conflict and each judgement call on its own, with a recommendation.

Two rules settle most conflicts:

- **Recency wins.** A product in this order that differs from an existing Pin
  is usually a switch you already made with your own money. The order in hand is
  the newest evidence, so it is the proposal; the existing product becomes an
  `alternate`. Two products for one slug in the same order are a conflict.
- **Explicit recipe text overrides recency.** A Recipe reading *"pre-cooked
  green or Puy"* at 250g names Merchant Gourmet's exact product, and that beats a
  more recent tin of something else.

### 8. Write the confirmed Pins

`confirmed: true` on anything a human agreed to; a hand-authored Pin is born
confirmed, since there is no guess to check. **Propose changes to an existing
Pin; never overwrite one.** A Pin already `confirmed: true` is a decision, and a
fresh harvest is evidence, not authority.

A Pin needs no product. The counter proteins have no line number and never will;
a **Staple** may have none yet because you last bought it before the harvested
window. Both are still Pins, because "store-cupboard, do not shop for it" is a
decision worth storing. **Unpinned** stays the absence of a row.

### 9. Account for everything

Record the **bought, matched nothing** list — harvested products binding to no
slug. Evidence that the corpus is missing a Recipe, not candidates for a Pin.

## Completion criterion for minting

**Every distinct slug in `Recipes/` is either Pinned or listed as an absence
with its reason.** Not most of them. Report the three counts: Pins written,
absences recorded, products that matched nothing.

## What this cannot cover

- **The proteins.** Chicken, eggs, steak and honey come from Soutars; fish from
  Dorset Meats. Neither sells online, so those Pins are authored by hand. The
  only Waitrose fish in the corpus is the fakeaway's frozen lemon sole.
- **An order is the household shop, not the meal plan.** Captures include
  toilet roll, washing liquid, supplements and fruit no Recipe uses. Harvest
  every line anyway; filtering to Recipe ingredients happens when Pins are
  minted, where the judgement is visible and correctable.
- **Permanence.** Line numbers churn — reformulation, delisting, seasonal lines
  — at an unestablished rate. Stored numbers need revalidation; that question is
  open on
  `.scratch/meal-planning-system/issues/09-harvesting-past-orders.md`.

## Known repo state

`Orders/history.md` is the harvest log. No order is stored in the repo: the four
orders harvested through 16 September were captured as files before this
procedure changed, and those files lived only on one machine. `PINS.md` is the
only thing a harvest leaves behind.
