# The Query String Generator

Type: prototype
Status: resolved
Blocked by: 04

## Question

Do the 44 stored `search_term`s actually resolve in Waitrose Multi-search, and
what happens when one misses?

**This ticket was rewritten.** Its original question — how a canonical
ingredient name becomes a search term, and whether that term is stored on the
Pin or derived by rules — **is already answered.** `search_term` is a stored
Pin field holding the harvested product name verbatim, decided in
[Mint The Pin Catalogue](11-mint-the-pin-catalogue.md) and written in
[Confirm And Write The Pins](13-confirm-and-write-the-pins.md). Coverage was
measured at **44 of 44 shoppable Waitrose Pins, with a `line_number` on every
one of them.** The ticket's second half — the output shape — was settled by
[What The Four Skills Are](08-what-the-four-skills-are.md): a pasteable
`search_term` block, with line numbers beside the table above it.

What was never tested is the thing the whole design rests on.

- **Paste the block and see.** Take the 44 terms and run them through
  Multi-search. How many resolve to the intended product, first hit?
- **Characterise the misses.** [Can Claude Drive
  Waitrose](01-can-claude-drive-waitrose.md) measured naive terms at 1 in 7 and
  found that wrong matches surface silently — a harvested product name is a much
  stronger input than a recipe word, but "stronger" is not "verified".
- **Decide the fallback.** A term that misses has a `line_number` that resolves
  directly at `/ecom/products/x/<n>`. Is the fix a per-Pin `search_term` edit, a
  link for that one item, or something else? A bad match must stay a one-line
  correction, not a rule change that perturbs the other 43.

Read the boundaries in `Orders/HARVEST.md` before driving a browser at Waitrose.
Search paths are `Disallow`ed; Multi-search is a normal navigation the user
clicks, which is why it is fine.

## Answer

**The terms resolve. The gap is quantity, not relevance.** 34 harvested
`search_term`s pasted into Multi-search against a real Plan — the week of
2026-09-14, Menu 1 — and **every one returned its intended product**. The
design assumption the whole project rests on holds.

Set against [Can Claude Drive Waitrose](01-can-claude-drive-waitrose.md)'s 1
in 7 for naive recipe words, that is the harvest earning its keep: a harvested
product name is not merely a stronger input, it is a **sufficient** one.

### Multi-search carries no quantity, and that is the real finding

The paste adds **1 of everything**. There is no quantity syntax, so counts are
a second pass the user makes by hand. On this Plan, 13 of 34 lines needed a
count above 1 and 21 were already right.

That was buried in the `Buy` column of a 34-row table — a column you read while
shopping, not while pasting. `bin/shopping-list.py` now emits a **counts block**
directly beneath the paste block: only the lines needing a change, largest
first, with their line numbers, and a plain statement of how many are correct
at 1. `divide()` already computed the count and `build()` was discarding it;
the change threads it through and renders it.

### The fallback was never needed, so it stays unchanged

No term missed, so nothing had to be corrected. The per-Pin `search_term` edit
versus per-item link question the ticket posed is therefore **still untested** —
but it is also no longer urgent, and the machinery is in place either way: every
row already carries its `line_number`, and `/ecom/products/x/<n>` resolves on
its own. Leave the choice to the first real miss, which will name its own case
better than speculation can.

### A correction worth recording

The first read of this test-run **reported two silent mismatches** — limes
resolving to lemons, and the Greek yogurt resolving to a smaller tub — and
generalised them into a pattern: *a longer product name losing to a shorter
sibling.* Two data points, one confident mechanism, a named failure mode.

**All of it was wrong.** The user had deliberately chosen a different yogurt,
and the duplicate lemons were their own slip while assembling the basket.
Neither was Multi-search. The pattern was invented to explain deviations that
had no search-side cause at all, and it would have gone into the map as a
finding had the user not said so.

The lesson generalises past this ticket: **a basket differs from a list for
many reasons, and search relevance is only one of them.** Reading a diff
between what was asked for and what is present cannot distinguish a bad match
from a human edit — only asking can. Ticket 23 got this right by measuring
before accepting its own framing; this ticket got it wrong by accepting a
framing it had authored itself, which is the harder case to catch.

The one thing that survives is weaker and truer: a basket is assembled by hand,
so it **can** drift from the list, and this run drifted twice. The script now
closes with the trolley's expected line count and points at the Line column as
the way to settle any row in doubt — a reconciliation aid, making no claim
about why a row might differ.

### Verified

- 34 of 34 terms resolved to the intended product
- counts block reproduces the 13 lines derived by hand, and the 21 at 1
- Menu 1 still **39 lines**, Menu 2 still **42**, **0 flags**, **0 Recipe/Pin
  rule violations** across 37 Recipes
- the Plan regenerates idempotently and its week note survives above
  `## Shopping`
