# The Query String Generator

Type: prototype
Status: open
Blocked by: 04

## Question

How does a canonical ingredient name become a search term that actually finds
the right product?

[Can Claude Drive Waitrose](01-can-claude-drive-waitrose.md) found this is
where all the remaining leverage sits. Waitrose search is bad in a *specific,
learnable* way, and the project controls the input entirely:

| Naive term | Result | Better term | Result |
| --- | --- | --- | --- |
| `Fage 2%` | 1104, wrong | `Fage Total 2` | 9, right |
| `pre cooked lentils` | 605, qualifier ignored | ? | ? |
| `cottage cheese` | 65, cream cheese at 1 and 3 | ? | ? |

Prototype the transformation against all seven researched ingredients plus a
sample from the real corpus, and find the rules: punctuation stripping, brand
placement, dropping qualifiers search ignores, adding words that discriminate.

Settle whether the search term is **a field on the Pin** (learned once, stored,
correctable by hand) or **derived** from the canonical name by rules. Storing it
is likely right — it makes a bad match a one-line fix rather than a rule change
that perturbs every other ingredient.

Then decide the output shape: one multi-search deep link for the whole week, one
link per ingredient, or a pasteable newline-separated block. Multi-search takes
a pasted list, so the pasteable block may beat any URL scheme.
