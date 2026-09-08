# The Query String Generator

Type: prototype
Status: open
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
