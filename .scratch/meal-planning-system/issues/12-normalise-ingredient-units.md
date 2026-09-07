# Normalise Ingredient Units

Type: task
Status: open
Blocked by: 07, 13

## Question

Rewrite every ingredient in the extracted Recipes into the unit its Pin
declares.

Split out of [Extract The Corpus](07-extract-the-corpus.md), which cannot do
this: it needs a Pin catalogue that did not exist when it was written. That
ticket transcribes quantities **verbatim** from the corpus and leaves them.

### The work

- **Unit normalisation.** The same ingredient is written in several units
  across the corpus — cannellini beans as `1 can`, `150g`, `240g` and `300g`;
  chicken breast as both a count and a mass; lentils as `1 pack` and `250g`.
  Each must end up in its Pin's single declared unit.
- **Split the one `or`.** `150g cannellini or haricot beans` becomes one
  ingredient; haricot moves to that Pin's `alternates`.
- **Flag the Unpinned.** Any ingredient with no Pin is flagged, never guessed.
  That list is a real output — it is what the weekly loop shrinks.

### Done when

Every ingredient in `Recipes/` is written in its Pin's declared unit or is
explicitly flagged Unpinned; no `or` remains; and shopping-list aggregation is
plain addition, so a Recipe disagreeing with its Pin is a detectable error
rather than a silent miscount.
