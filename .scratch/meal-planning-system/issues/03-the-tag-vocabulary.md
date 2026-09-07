# The Tag Vocabulary

Type: grilling
Status: resolved
Blocked by: 02

## Question

Which tags exist on a Recipe, and what does each one mean?

Candidates raised so far: side dish, eat-cold, quick, unhealthy, bulk-cook,
fakeaway. Plus the protein-type axis that `GOALS.md` already plans against —
sausage, egg, tofu, chicken, white fish, oily fish, beef.

The real questions underneath:

- Is protein type a **tag** or its own field? `GOALS.md` counts against it
  ("3x Tofu Lunch, 2x White Fish Dinner"), so menu generation must query it
  precisely. A free-form tag makes that query fragile.
- Is slot (breakfast/lunch/dinner/pudding) a tag, a field, or implied by where
  the file sits? Several meals appear in more than one slot across the corpus.
- Does "unhealthy" earn its place, given every recipe already carries protein
  and kcal? A tag that duplicates data you already have is a liability.
- Is the vocabulary closed? An open one drifts — "quick" and "fast" both
  appearing means generation silently misses half the pool.

Settle the list, settle whether it's closed, and write it down.

## Answer

**Five closed vocabularies, four of them fields.** Protein type and slot are
fields, not tags. `unhealthy`, `quick` and `side-dish` are rejected. Every
vocabulary is closed and enforced: an unrecognised value is an error, not a
new member.

### The vocabulary

| Field | Cardinality | Values |
| --- | --- | --- |
| `slot` | one | `breakfast` `lunch` `dinner` `pudding` |
| `protein` | one | `sausage` `egg` `tofu` `quorn` `chicken` `white-fish` `oily-fish` `beef` |
| `effort` | one | `low` `medium` `high` |
| `appliances` | list | `skillet` `air-fryer` `ninja-sizzle` `rice-cooker` `pot` `toaster` `poacher` |
| `tags` | list | `fakeaway` `bulk-cook` `eat-cold` |

**Tag meanings — all three are capability, never intent.** What a real week
actually did belongs to a Plan, not to the Recipe.

- `fakeaway` — restaurant-style dish cooked at home.
- `bulk-cook` — can be cooked 4+ portions in one go.
- `eat-cold` — fit to eat cold the next day, where no reheat is available.

### Three standing rules

1. **Closed and enforced.** Unrecognised value = error.
2. **Extend on first real use**, as a one-line edit. Do not pre-stock values
   nothing cooks. (`beans` is deliberately absent for this reason.)
3. **`lower-kebab-case`** throughout, matching the `ingredient:` keys and the
   filename-as-identity rule from
   [What A Recipe File Looks Like](02-what-a-recipe-file-looks-like.md).

### Why protein is a field

`GOALS.md` counts against it precisely ("3x Tofu Lunch, 2x White Fish Dinner"),
so it must be queryable exactly; a free-form tag makes that a string match
against an open vocabulary. Single-valued because the fakeaway burger carries
chicken *and* halloumi and the steak pilaf carries beef *and* parmesan, but
only one of those is what the layout counts.

It also cannot be inferred from the title. `Creamy Gochujang & Sweetcorn White
Bean Skillet` (W2 Sunday lunch) contains **2 chicken breasts**. Titles may be
rewritten later, but the field is what generation reads either way.

`quorn` is retained as a sanctioned value despite having zero members today —
an explicit exception to rule 2, so a later session doesn't re-litigate whether
Quorn counts as its own protein or as `chicken`. It must not be `chicken`:
that would satisfy "1x Chicken Dinner" and silently consume a meat slot.

### Why slot is a field

Checked, not assumed: across all 47 meal instances in both weeks, **no recipe
appears in more than one slot**. Every recurring recipe recurs in the same slot
every time. The near-miss pairs are distinct recipes with distinct ingredients
(`Lemon, Herb & Lentil Chicken Pan` vs `Lemon, Herb & Lentil Tofu Pan`).

This ticket's own question asserted the opposite. Not a folder, because
folder-as-data makes re-slotting a rename and collides with
[Where Everything Lives](05-where-everything-lives.md).

### Why `appliances` was pulled into this ticket

The field was already drifting badly — **14 distinct spellings for 8
appliances**:

| Appliance | Spellings in the corpus |
| --- | --- |
| skillet | `One Skillet` x14, `Skillet` x4, `Pan` x1 |
| air-fryer | `One Air Fryer Basket` x7, `Ninja Air Fryer` x3, `Air Fryer` x3, `One Air Fryer Basket + One Bowl` x1 |
| ninja-sizzle | `Ninja Sizzle` x5, `Ninja Sizzle Plate` x3, `Sizzle Plate` x1 |
| rice-cooker | `Rice Cooker` x4 |
| pot | `Pot` x3 |
| toaster | `Toaster` x2 |
| poacher | `Poacher` x1 |

This is precisely the drift this ticket raised as a hypothetical for tags
("quick and fast both appearing") — except it had already happened in a
neighbouring field and nobody had noticed. "No three-appliance dinners on a
weeknight" is unanswerable against that table today. Splitting "which
vocabularies are closed" across two tickets is how one ends up open by
accident, so it is settled here.

`Bowl` is not an appliance and is dropped. `Pan` collapses into `skillet`.

### `effort` — and why it replaces `quick`

A Claude-generated judgement of how complicated the recipe looks, on
`low` < `medium` < `high`. It replaces the rejected `quick` tag: same question,
but with a scale and a rubric instead of a boolean somebody has to adjudicate.

**Written once at Recipe creation and stored, never recomputed.** A value
regenerated per session would drift, and "no high-effort dinners on a weeknight"
would stop meaning anything. It is a decision, recorded — the same treatment a
Pin gets.

**Signals, not a formula.** Ingredient count, step count and appliance count
across the 37-recipe corpus band cleanly:

- `low` — ~4 or fewer ingredients, 0-1 appliances. All four puddings, plus
  `Eggs and Soldiers`, `Eggy Bread`, `Zero-Prep Sausage & Chickpea Crisp Hash`,
  `Smashed Avocado & Soft Poached Eggs`.
- `medium` — 5-7 ingredients, 1-2 appliances. The bulk of the corpus; most
  lunches and the simpler dinners.
- `high` — 8+ ingredients or 3 appliances. Most dinners, topped by
  `The "Fakeaway" Peri-Peri Chicken Burger` at 12 ingredients, 6 steps,
  3 appliances.

Judgement overrides arithmetic where they disagree, which is why this is not a
formula: `Savory Egg, Avocado & Homemade Baked Bean Skillet` has 9 ingredients
but cooks in **one skillet** in 5 steps, and is genuinely easier than
`Korean Gochujang Glazed Chicken` at 8 ingredients across **3 appliances**.
Count the pans and the parallelism, not just the shopping list.

### Rejected, with reasons

- **`unhealthy`** — restates `protein_g` and `kcal`, which every recipe already
  carries. A tag that duplicates a number drifts when the number is corrected.
  The two dishes it would plausibly land on are the fakeaways, already marked.
- **`quick`** — superseded by `effort`. As a boolean it was also derivable from
  `appliances` length, making it the same liability as `unhealthy`.
- **`side-dish`** — no such recipe exists. The corpus bundles sides into the
  main; even `The Combo Lemon Sole Plate` carries its own chips and salad.
- **`vege` / `meat-free`** — dropped entirely by the user as complexity not yet
  paying for itself. See the premise correction below for what it would have
  meant.

### Premise corrections recorded while resolving

1. **The corpus is 37 unique recipes, not 28.** `CLAUDE.md` says 28. Actual:
   13 breakfast, 8 lunch, 12 dinner, 4 pudding. 33 excluding puddings.
2. **No recipe appears in more than one slot** — see above. This ticket
   asserted several did.
3. **`GOALS.md`'s lunch layout matches neither existing week.** It asks for
   3x Tofu + 2x Chicken. Week 1 ran 2 tofu / 4 chicken; Week 2 ran 5 tofu /
   1 chicken. Both weeks have **6 lunches, not 5** — Saturday has no lunch in
   either week. Evidence for
   [Per-Slot Macro Bands](06-per-slot-macro-bands.md); do not silently correct
   it, exactly as with the ganache.
4. **Every dinner in both weeks contains meat or fish.** All twelve. This is
   why "no recipe satisfies Vege Meal" was true — the Vege Meal was a *dinner*
   goal, and dinner is the only slot with zero meat-free entries. Recorded
   because it is the fact that would be re-derived if vege is ever revived.
5. **Saturday has only breakfast in both weeks, and Friday has no pudding.**
   `CONTEXT.md` says a Menu is complete — "every day, every slot, filled".
   The corpus disagrees. Belongs to Per-Slot Macro Bands or
   [Extract The Corpus](07-extract-the-corpus.md).

### Consequences

- `GOALS.md` loses its `1x Vege Meal` line. **Done as part of this resolution.**
- `CONTEXT.md` gains Protein Type, Tag, Appliance and Effort as glossary terms —
  what each *is*, without the value lists. **Done.**
- [Where Everything Lives](05-where-everything-lives.md) inherits an explicit
  obligation: give this vocabulary a home file. Content is settled here;
  location is that ticket's call.
- [Extract The Corpus](07-extract-the-corpus.md) inherits appliance
  normalisation (14 spellings to 7 values across 37 recipes) and assigning
  `effort` to all 37.
- New fog: how a Plan records *acting on* `bulk-cook` or `eat-cold`, since the
  doubled quantities have to reach the shopping list somehow.
