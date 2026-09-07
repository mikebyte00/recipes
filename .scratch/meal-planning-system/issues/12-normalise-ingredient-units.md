# Normalise Ingredient Units

Type: task
Status: resolved
Blocked by: 07, 13 — both resolved

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

## Answer

**Done, 07 September 2026.** 248 ingredient lines across 37 Recipes now satisfy
a single rule, stated in [PINS.md](../../../PINS.md#what-a-recipe-may-write):
either the line's `unit` equals its Pin's `unit`, or the line has no `qty` and
its Pin says `staple: true`. Nothing else passes, so a Recipe disagreeing with
its Pin is detectable rather than a silent miscount.

### This ticket was scoped too small

It described unit normalisation plus one `or`. Two resolved tickets had quietly
assigned it three more jobs, and neither the ticket nor the corpus matched the
numbers in circulation:

| Job | Assigned by | Believed | Actual |
| --- | --- | --- | --- |
| Unit normalisation | here | 13 slugs | **8** |
| Split the `or`s | 07, bug 4 | 1, then ~12 | **13** |
| Strip `staple:` from recipes | 07, hole 3 | — | 61 lines |
| Decide the near-duplicate slugs | 11, decision 2 | — | 7 pairs |
| Flag the Unpinned | here | 18 | **17** |

The "13 of 112 slugs" in circulation is ticket 11's count of slugs carrying
**more than one unit**, which is a different set from slugs disagreeing with
their Pin. The real mismatch list is 8 quantified slugs, plus 9 staples written
with no `qty` and no `unit` at all — a case no ticket had named.

### Decisions

1. **`water` is deleted from the Recipes**, all five lines. Stripping `staple`
   would have made it Unpinned and so flagged for manual buying, which is
   absurd; Pinning it violates
   [Mint The Pin Catalogue](11-mint-the-pin-catalogue.md)'s decision 5. Every
   method already says "a splash of water". An ingredient that can never be
   bought and can never be summed was carrying nothing. This retires the
   "not a purchasable thing" absence, and the Absences list is now 17.

2. **A staple may legally omit both `qty` and `unit`.** This answers
   [Extract The Corpus](07-extract-the-corpus.md)'s fourth format hole for the
   19 staple lines — `olive-oil` x9, `oil-spray` x5, `butter`,
   `smoked-paprika`, `truffle-oil` and the mayonnaises. They never reach a
   shopping list, so a quantity would be invented precision. **The six
   non-staple blanks were given quantities** — `tartare-sauce` 40g, `oat-milk`
   60g, `halloumi` 100g, `lettuce` 40g, `pineapple` 60g, `waffle-fries` 300g —
   because a list cannot add a blank. Those are estimates, in a project whose
   macros already are.

3. **Five near-duplicate pairs merged, two kept.** 11 left this here "with the
   recipes in front of it", and with them in front of it:

   | Pair | Verdict |
   | --- | --- |
   | `baby-spinach` -> `spinach` | Merged. One product, one line number |
   | `wholegrain-rice` -> `brown-rice` | Merged. One product |
   | `mixed-salad-greens` -> `rocket` | Merged; `1 bag` became `100g`, the pack size. The Pin's `display` is now **Babyleaf & rocket salad**, which is what the product is and covers both uses |
   | `new-potatoes` -> `baby-potatoes` | Merged. `potatoes` — the chipping bag, a different line number — stays separate |
   | `dried-italian-herbs` -> `dried-herbs` | Merged. Both generic, both staple |
   | `parsley` / `dried-parsley` | **Kept.** Genuinely different products |
   | `lemon` / `lemon-juice` | **Merged — see 4** |

4. **Juice folded into fruit.** `lemon` was counted in units and `lemon-juice`
   measured in grams, both Pinned to the same product, so a list could never
   add them. Folded at **20g juice = half a lemon** and **20g = two-thirds of a
   lime**, which turns seven unaddable lines into "Lemons, 5". Recipes keep
   `prep: juiced`, so nothing is lost at the hob.

5. **Three Pin units looked wrong and were left alone; the Recipes moved.**
   `dried-oregano` is `unit: g` while `dried-parsley` is `unit: pinch`, and one
   recipe wrote a pinch of oregano; `curry-powder` is `g` and one recipe wrote
   1 tsp; `sirloin-steak` is `g` with no bridge, yet one recipe wrote "2". The
   Pins were confirmed by hand the day before and are authoritative, so the
   conversions went into the Recipes — pinch to 0.5g, 1 tsp to 2g, 2 steaks to
   300g, which is what the *other* steak recipe already said. **`sirloin-steak`
   gained `each_g: 150`** so the bridge exists next time.

6. **Eleven substitutions moved to their Pin's `alternates`** and left the
   Recipes: Quark, tamari, maple syrup, haricot beans, Moroccan spice blend,
   Italian seasoning, garlic powder, and the green/Puy lentil pair the Pin's
   own product already spans. **Three `or`s deliberately remain**, and none is
   a substitution the Pin can hold:

   - `eggs prep: soft-boiled or poached` — a cooking choice, not a shelf one.
   - `burger-buns note: brioche or wholemeal` — **Unpinned**, so there is no
     `alternates` to move it to.
   - `wholewheat-linguine note: ... spaghetti` — likewise Unpinned. The note now
     says why it stays.

   Unpinned ingredients having nowhere to record a substitute is a real gap in
   the model, not an oversight here. It resolves itself: buying either one puts
   it in the order history, and the next harvest Pins it.

### The Unpinned flag

**17 of 104 slugs**, and [PINS.md](../../../PINS.md#absences)'s Absences section
is now explicitly that list rather than a coverage note. 14 are real shopping
items never seen in the three captured orders; 3 are fresh things deliberately
not stapled. Each Pins itself on the next harvest after you buy it — which is
the loop this list exists to shrink.

### Not done here

**No validator was written.** The rule is checkable and stated, but the repo
has no code and no decided place to put any; inventing a `bin/` in passing is
exactly the kind of shape decision this map keeps asking sessions not to make.
It belongs to [What The Four Skills Are](08-what-the-four-skills-are.md), whose
shopping-list skill has to apply the rule anyway.
