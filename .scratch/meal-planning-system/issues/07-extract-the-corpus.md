# Extract The Corpus

Type: task
Status: open
Blocked by: 02, 03, 04, 05

## Question

Convert the two existing rotations into the Recipe pool and two Menus.

Roughly 28 distinct meals across `Rotations/Week1.md` and `Rotations/Week2.md`,
with real duplication to resolve: Warm Tofu, Chickpea & Feta Salad Pan appears
in both weeks; Creamy Pesto Chicken & Cannellini Beans and Lemon, Herb & Lentil
Chicken Pan each appear twice within Week 1; the puddings recur throughout.

Deduplicate against the identity rule settled in
[What A Recipe File Looks Like](02-what-a-recipe-file-looks-like.md), tag every
Recipe against [The Tag Vocabulary](03-the-tag-vocabulary.md), canonicalise
every ingredient per
[How Ingredients Are Named](04-how-ingredients-are-named.md), and file it all
per [Where Everything Lives](05-where-everything-lives.md).

Done when both Menus reference pooled Recipes, no meal content is lost, and a
spot check of a converted week reproduces the original document's macros.

Record anything the conversion could not represent — that list is the real
output of this ticket, and it is what will expose a hole in the format before
any skill is written against it.

## Known data fixes, found while prototyping the format

- **The Raspberries & White Chocolate Ganache** exists in two sizes across both
  weeks. This is an error. Keep the standard — 200g Fage, 24g white chocolate,
  ~170 kcal, ~11g protein — and drop the 300g/40g version. Recompute the Sunday
  totals in both weeks rather than copying the originals.
- **Sizzled Sirloin Steak** lists brown rice but its method says "the raw rice
  or quinoa", and the truffle oil named in its own title appears in no
  ingredient list. Add every ingredient the method needs.
- **Salt, pepper, oil spray and water** appear in methods throughout but in no
  ingredient list. Recipes now list everything; the Pin's staple flag filters
  the shopping list.
- **Unit normalisation.** The same ingredient is written in several units
  across the corpus — cannellini beans appear as `1 can`, `150g`, `240g` and
  `300g`; chicken breast as both a count and a mass; lentils as `1 pack` and
  `250g`. Every ingredient must end up in the single unit its Pin declares.
- **Split the one `or`.** `150g cannellini or haricot beans` becomes one
  ingredient; haricot moves to that Pin's `alternates`.

## Comments

**Two more items inherited from [The Tag Vocabulary](03-the-tag-vocabulary.md).**

- **Normalise `appliances`.** The corpus uses **14 distinct spellings for 8
  appliances** (`One Skillet` / `Skillet` / `Pan`; `One Air Fryer Basket` /
  `Ninja Air Fryer` / `Air Fryer`; `Ninja Sizzle` / `Ninja Sizzle Plate` /
  `Sizzle Plate`). All collapse to the closed enum
  `skillet, air-fryer, ninja-sizzle, rice-cooker, pot, toaster, poacher`.
  `Bowl` is not an appliance and is dropped.
- **Assign `effort`** (`low`/`medium`/`high`) to all 37 recipes. Written once
  and stored, never recomputed. The banding and the judgement rule — pans and
  parallelism over raw ingredient count — are in that ticket's `## Answer`.

**Also: the corpus is 37 recipes, not 28.** 13 breakfast, 8 lunch, 12 dinner,
4 pudding. Size this ticket against 37.

**Two facts to preserve rather than fix**, alongside the ganache correction:
`GOALS.md`'s lunch layout matches neither week (asks 3 tofu / 2 chicken;
Week 1 ran 2/4, Week 2 ran 5/1, and both weeks have 6 lunches, not 5), and
Saturday carries only breakfast in both weeks while Friday has no pudding —
which contradicts `CONTEXT.md`'s "a Menu is complete". Both are evidence for
[Per-Slot Macro Bands](06-per-slot-macro-bands.md).

---

**Target layout, from [Where Everything Lives](05-where-everything-lives.md).**

- Recipes to `Recipes/<slug>.md`, **flat** — no sub-folders. Filename is
  identity; `slot` and `protein` stay frontmatter fields and must not be
  duplicated into the path.
- The two rotations become `Menus/menu-1.md` and `Menus/menu-2.md`, structured
  references to Recipe slugs, **no prose and no inlined recipe bodies**.
- **Delete `Rotations/` as the final step, once the extraction is verified.**
  This is an explicit step, not a tidy-up: leaving it makes the repo carry a
  third source of truth for every recipe, which is how the ganache discrepancy
  survived unnoticed. Deleting it before verification loses the only source if
  the extraction is wrong.

`VOCABULARY.md` at the root is the operative list of legal field values.
