# Harvesting Waitrose orders

**ALWAYS** prefer to use Claude Chrome extention to control a real browser. Avoid using in-built browser

How to capture a completed Waitrose order into this repo, with **line numbers**.
Reusable: run it whenever new orders have landed. It skips what is already
captured, so re-running is cheap and safe.

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
already signed in to, reads what is on screen, and writes files in this repo.

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
and nothing else.** Driving the basket stays parked; see
`.scratch/meal-planning-system/issues/01-can-claude-drive-waitrose.md` before
extending anything here.

## Scope

**Completed orders dated 1 August 2026 or later.** Skip cancelled orders — they
have no items. Ignore anything earlier; it predates the two-week corpus.

## Steps

### 1. Find what is missing

Read `Orders/history.md` for what is already captured, then open **My Orders**
and read the order list. An order needs harvesting when it is completed, dated
1 August 2026 or later, and has no file in `Orders/`.

Name files `<DD>-<month>.md`, lowercase — `11-august.md`.

### 2. Capture each missing order

Open the order's detail page and **scroll to the bottom before extracting** —
the item list lazy-loads, and un-scrolled products are silently absent.

Read the item rows for name, pack size, quantity and price. Then run this to
get the line numbers:

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

Join the two on product name. The snippet encodes an assumption about markup
that Waitrose may change — if it returns nothing, or the wrong text, adapt the
selector. **The completion criterion below is what matters, not this snippet.**

### 3. Write the order file

One file per order, following `Orders/11-august.md`. Keep Waitrose's own
section headings (Food Cupboard, Fresh & Chilled, Frozen, Bakery, Household,
Toiletries) — they are the closest thing to a free product taxonomy.

```markdown
# Waitrose Order — 11 August 2026

Order number 1000000001. Collected Tuesday 11 August, 10:00am–11:00am, from Riverside, AB1 2CD.

### Food Cupboard

| Line | Item | Size | Qty | Cost |
|---|---|---|---|---|
| 584333 | Epicure Organic Cannellini Beans | 400g | 1 | £1.20 |
| — | Some Product With No Resolvable Link | 250g | 1 | £2.00 |

### Cost breakdown

- Item total: £123.29
- Savings: −£0.70
- **Total: £122.59**
```

Two rules that make the file usable later:

- **Record product names exactly as Waitrose writes them.** A tidied name breaks
  the join and destroys the naming evidence the harvest exists to collect.
- **Write `—` in the Line column when no number resolves.** An unresolved
  product is *Unpinned*: flagged for a human, never guessed. A plausible-looking
  wrong number is the one failure this whole design is built to avoid.

### 4. Update the index

`Orders/history.md` holds the order list — date, status, total, and whether it
has been captured. Add a row per order seen, including cancelled ones, so a
later run knows they were considered and skipped rather than missed.

### 5. Verify before reporting done

Spot-check **five** line numbers per order by opening
`/ecom/products/x/<number>` and confirming the product name and pack size match
what was recorded. This is an allowed path and the only check that catches a
mis-joined row.

## Completion criterion

Every completed order dated 1 August 2026 or later has a file in `Orders/`;
every item in every new file carries either a line number or `—`; every new
order appears in `Orders/history.md`; and five numbers per new order have been
verified against their product page.

Report the count of items harvested and the count left `—`.

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

`Orders/31-august.md` currently holds both the order-history index and the
31 August detail, and no order file yet carries a Line column. First run should
split that file into `Orders/history.md` plus a clean `Orders/31-august.md`,
and backfill line numbers into the three August orders.
