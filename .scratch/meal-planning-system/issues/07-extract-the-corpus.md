# Extract The Corpus

Type: task
Status: resolved
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
**Deferred to [Normalise Ingredient Units](12-normalise-ingredient-units.md):**
unit normalisation and the `or` split both require a Pin catalogue, which does
not exist yet. **Transcribe quantities verbatim from the corpus** — `1 can`
stays `1 can` — and leave them. Recording the inconsistency is useful; guessing
at a unit before its Pin declares one is not.

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

## Answer

**37 Recipes in `Recipes/`, 2 Menus in `Menus/`.** Every vocabulary value legal,
every macro reproducing the corpus, every Menu reference resolving, no orphans.

### Verification

- 37 corpus titles → 37 files. None missing, none invented.
- **Every `slot`, `protein`, `effort`, `appliance` and `tag` value validates
  against `VOCABULARY.md`.** Zero violations.
- Slots: 13 breakfast, 8 lunch, 12 dinner, 4 pudding. Effort: 10 low,
  19 medium, 8 high.
- **Every recipe's macros match its corpus figures exactly**, including the
  ganache, which now carries the standard 200g/24g values.
- All 56 Menu slots resolve to real Recipe files. 37 of 37 Recipes are
  referenced; nothing is orphaned.

`Rotations/` is **retained** pending sign-off. Deleting it is the final step.

## Format holes — the real output

Ranked by how much they need answering before a skill is written.

### 1. Puddings have no `protein`, so the field must be optional

The enum has no dairy or yogurt value and `GOALS.md` counts protein type only
for breakfast, lunch and dinner. All four puddings were written **without a
`protein` key**.

[The Tag Vocabulary](03-the-tag-vocabulary.md) did not say the field was
optional. It now must be, or puddings need an enum value nothing counts.
**Needs ratifying.**

### 2. The `~` cannot survive into YAML

`CLAUDE.md` says every macro carries `~` and to keep it, because the numbers are
estimates. **`protein_g: ~32` is not valid YAML** — `~` is null there.

[What A Recipe File Looks Like](02-what-a-recipe-file-looks-like.md) already
dropped it in its own example without remarking on it. So the tilde now lives in
documentation and rendering, never in the data. That is a **direct conflict with
a standing constraint** and should be settled explicitly rather than by
accident.

### 3. `staple: true` sits on the ingredient, contradicting a resolved decision

[How Ingredients Are Named](04-how-ingredients-are-named.md) puts the staple
flag **on the Pin**. Pins do not exist yet, so staples added during extraction
were marked on the recipe ingredient instead.

**This is a second source of truth and should not survive.**
[Mint The Pin Catalogue](11-mint-the-pin-catalogue.md) should move the flag to
the Pin and [Normalise Ingredient Units](12-normalise-ingredient-units.md)
should strip it from the recipes.

### 4. There is no way to say "quantity unknown"

Several ingredients carry no quantity in the corpus at all — oat milk in
`Eggy Bread`, sweetcorn in the gochujang skillet, and most of the fakeaway
burger (lettuce, halloumi, pineapple, both mayos, waffle fries), plus tartare
sauce and salad greens in the lemon sole plate. These were written with a `note`
and no `qty`. A real representation may be wanted, since a shopping list cannot
add up a missing number.

### 5. A Menu cannot be complete

**4 of 28 slots are `null` in each Menu** — Saturday lunch, dinner and pudding,
and Friday pudding. `CONTEXT.md` says a Menu is never partial. The corpus
disagrees, and the gap is inherited rather than introduced. Evidence for
[Per-Slot Macro Bands](06-per-slot-macro-bands.md).

## Data bugs found during extraction

Beyond the five already known to this ticket.

1. **`Creamy Mild Curry Tofu & Butter Beans` cooks chicken.** Its method opens
   "Fry chicken mini fillets" — in a tofu recipe with no chicken in it. A
   copy-paste error, corrected to tofu during extraction. The same class of bug
   as the gochujang lunch that was named for a bean and built on chicken.
2. **`Moroccan Spiced Chicken` is a macro outlier and uses a different label.**
   `**Total Plate Profile**` rather than `**Nutrient Profile**`, and ~75.5g
   protein against ~42–49g for every other dinner. It drives Week 2 Tuesday to
   ~168.9g protein against a 130–140g target. Transcribed as-is; flagged for
   Per-Slot Macro Bands.
3. **`*The Plate:` is a 15th appliance spelling.** Two recipes label the field
   `The Plate` rather than `The Pan`. The earlier count of "14 spellings for 8
   appliances" **missed both recipes entirely**, because the grep matched only
   `The Pan`. The label drifts, not just the values.
4. **There are roughly twelve `or`s, not one.** This ticket named
   `cannellini or haricot`. Also present: honey or maple syrup, soy sauce or
   tamari, parsley or dried herbs (twice), Italian herbs or garlic powder, green
   or Puy lentils, linguine or spaghetti, Greek yogurt or cottage cheese,
   soft-boiled or poached eggs, new or baby potatoes, cream cheese or Quark, Ras
   el Hanout or Moroccan spice blend. Each is preserved verbatim in a `note` for
   [Normalise Ingredient Units](12-normalise-ingredient-units.md) to split.
5. **Appliance lists disagree with methods.** `Sticky Miso-Glazed Fish` lists
   rice cooker and air fryer but its method chars pak choi on the sizzle plate;
   several recipes toast bread without listing a toaster. Appliances were taken
   from **what the method actually does**, not from the header.
6. **`Eggs and Soldiers` butters toast it never lists.** Added as a staple.
7. **The cheesecake lists one lemon as two ingredients** — "½ fresh lemon,
   juiced" and "Zest of ½ lemon". Merged into one entry.
