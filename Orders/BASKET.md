# Building the Waitrose basket

**ALWAYS** prefer to use the Claude Chrome extension to control a real browser.
Avoid the in-built browser.

How to fill the Waitrose trolley from a Plan's Waitrose table, by line number.
Reusable: run it whenever a Plan's shopping section is final and the week's
order is about to be placed.

Written for a browser-driving agent working in the user's own signed-in
session. A human can follow it too, but a human has a faster way — the
Multi-search block in the same Plan.

## What this replaces, and what it does not

The Plan already emits the two things this needs:

```
| Item             | Need  | Buy       | Line   |
|------------------|-------|-----------|--------|
| Cherry tomatoes  | 450 g | 3 × 200 g | 097155 |
```

The **Line** is the product and the **multiplier in Buy** is the quantity. `3 ×
200 g` means quantity 3 of line 097155 — the pack division already happened, at
list time, in `PINS.md`. **Never re-derive a quantity from the Need column.**

This covers the Waitrose table only. The **Unpinned** items — the ones the Plan
counts as "to add by hand" — have no line number and stay manual, through
Multi-search. Soutars and Dorset Meats are counter lists and are not online at
all.

## Boundaries

This procedure **writes**. It empties and fills a real trolley in a session the
user has already signed in to.

`robots.txt` disallows `/ecom/shop/trolley`. **The user overruled that on
14 September 2026**, on the same reasoning that covers `HARVEST.md`: this is a
person filling their own basket, in their own browser, at their own request —
not a crawler. The reasoning is theirs and it covers **the trolley page and
product pages, and nothing further**.

Three hard guardrails:

- **Never place an order.** Adding to the trolley is the end of this procedure.
  Checkout, payment and slot booking are the user's, always. If a page offers to
  complete an order, it is the wrong page — go back.
- **Never enter credentials.** If the site is signed out, stop and say so. Wait
  for the user; do not proceed on a guest session (see *Why the guest session
  matters* below).
- **Reach products by line number only** (`/ecom/products/x/<number>`), never by
  search. Search is `Disallow`ed and was measured resolving 1 ingredient in 7
  correctly.

## Steps

### 1. Confirm the session is signed in

Open any product page by line number and look for the account menu. **"Sign in"
visible means stop** — tell the user, wait, and resume only once they confirm.

### 2. Empty the trolley

Open `/ecom/shop/trolley` and use **Empty Trolley**. This is deliberate and it
is destructive: the Plan is the source of truth for the week, so the trolley
starts from nothing.

**Report what was in it first.** One line — item count and total — so a trolley
that held something unexpected is on the record before it is gone.

### 3. Add each line

For each row of the Plan's Waitrose table, in order:

1. Navigate to `/ecom/products/x/<line>`.
2. **Confirm the product name matches the Item column** before adding. The URL
   canonicalises itself, so the page tells you what the number really is. A
   mismatch is a stale Pin — record it, skip the row, do not substitute.
3. Set the quantity, then click **Add to Trolley**. Quantity is a typeable text
   box, so one type and one click does any quantity — there is no stepper to
   click repeatedly.

Two traps, both of which fail **silently**, which is why they are written down:

- **Setting the quantity programmatically does not work.** Assigning the input's
  value directly leaves the page's own state at 1, and the click then adds
  nothing at all — the button stays reading "Add to Trolley" and no error
  appears anywhere. Use real events: click into the field, select its contents,
  type the number.
- **The header trolley total lies.** It is stale for some seconds after an add
  and shows neither the old value nor the new one. Never verify against it.

### 4. Verify against the trolley page

Open `/ecom/shop/trolley` and read it. Check **the line count matches the table**
and **each quantity matches its multiplier**. The trolley page is the only
honest surface; per-line quantity inputs carry the real numbers.

### 5. Report

Say what was added, what was skipped and why, and what the user still has to add
by hand — the Unpinned items, with the Multi-search block from the Plan.

## Completion criterion

The trolley holds one line per row of the Plan's Waitrose table, each at its
Buy multiplier, verified on the trolley page and not the header; every skipped
row is named with its reason; and the order has **not** been placed.

## Why the guest session matters

Add-to-trolley was measured **failing silently as a guest** — the trolley stayed
at £0.00 and no network request fired. Signed in, the same action works
normally. That is the whole reason step 1 exists: a guest session does not
error, it just quietly does nothing, and a run that skips the check reports
success over an empty trolley.
