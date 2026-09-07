# Per-Slot Macro Bands

Type: grilling
Status: resolved
Blocked by: —

## Question

What are the per-slot protein and kcal bands that new Recipes must hit?

`GOALS.md` now carries daily targets — 130–140g protein, ~1800 kcal — but a
Recipe generator needs a per-slot budget or it produces meals that only add up
by luck.

The existing corpus already implies the bands. Observed across both rotations:

| Slot | Protein | kcal |
| --- | --- | --- |
| Breakfast | 17–32g | 295–490 |
| Lunch | 43–48g | 330–420 |
| Dinner | 42–58g | 695–800 |
| Pudding | 11–15g | 120–242 |

Note the tension worth grilling on: those daily totals run 118–169g protein and
1545–1862 kcal, so several existing days **miss** the new 130–140g target. Are
the bands wrong, is the target aspirational, or are the existing weeks simply
due a correction?

Resolve the bands and write them into `GOALS.md` next to the daily goals.

## Answer

**Four Bands, one per Slot, each a target plus a range. Written into
`GOALS.md`. The Bands guide generation; the goals are checked by summing a
day.**

| Slot | Target protein | Target kcal | Protein range | kcal range |
| --- | --- | --- | --- | --- |
| Breakfast | ~27g | ~420 | 17–32g | 295–490 |
| Lunch | ~45g | ~380 | 43–48g | 330–420 |
| Dinner | ~48g | ~730 | 42–58g | 695–800 |
| Pudding | ~12g | ~155 | 10–20g | 100–250 |
| **Day** | **~132g** | **~1685** | | |

### The tension, resolved

The ticket asked whether the bands are wrong, the target aspirational, or the
existing weeks due a correction. **The daily goals were mis-stated, and the
fix was to read them as a floor and a ceiling rather than a band and a target.**

Measured through both Menus, the twelve full days ran 117–156.5g protein and
1515–1788 kcal. Against `130-140g protein/day, ~1800 kcal/day` that is 6 of 12
compliant on protein and **0 of 12 on calories** — a corpus that fails its own
goals everywhere is evidence the goals are written wrong, not that 37 recipes
are.

- **Protein is a floor**, not a band. Overshoot costs nothing, because
  carbohydrates and fat are untracked and there is no budget for extra protein
  to blow. `~130g/day` as a minimum.
- **Calories are a ceiling**, not a target. Under is better than over. That
  turns 0/12 compliant into 12/12 without touching a single Recipe.
- Both are **rough objectives**. A day that misses is not a failure to correct.

### Bands guide; the day gates

A day assembled from the bottom of every range sums to ~113g, and one from the
top sums to ~1880 kcal. **Range-legal does not imply goal-compliant**, so the
check cannot live on the Recipe.

The alternative — narrowing the Bands until any legal combination satisfies the
day — was rejected. It needs breakfast's floor at ~25g and dinner's kcal
ceiling at ~750, which retroactively invalidates 5 existing Recipes, and it is
exactly the engineering-around-non-compliance that the "rough goals" answer
rules out.

Hence targets: a generator aiming at the middle of a wide range lands anywhere,
so each Band carries a figure to hit. The four targets sum to ~132g / ~1685
kcal, clearing the floor and sitting under the ceiling with headroom.

### Bands are per Slot, not per Slot × Protein Type

Only breakfast separates cleanly by protein type, and it separates completely:
egg breakfasts 17–27g, sausage breakfasts 29–32g, no overlap. Lunch and dinner
overlap heavily (tofu 43–46 vs chicken 43–48; white fish 42–49 vs chicken
47–58). Splitting all four Slots would yield 11 Bands derived from as few as
two Recipes each. Recorded as a documented note under breakfast instead.

### Pudding's range is widened, not measured

All four puddings sit in 11–13.5g / 120–170 kcal. That is four variations on
one idea (yogurt, fruit, something melted) rather than a bound on the Slot, so
the range was loosened to 10–20g / 100–250 kcal and `GOALS.md` says it was.

### Corrections made to the record

- **The ticket's own table was wrong on pudding**: it claimed 11–15g /
  120–242 kcal. Measured, the four puddings are 11–13.5g / 120–170. No recipe
  has ever been near 242.
- **`moroccan-spiced-chicken-with-air-fried-butternut-squash-flaked-almonds`
  was corrected from `protein_g: 75.5, kcal: 758` to `48 / 730`.** It claimed
  75.5g against 42–58g for all eleven other dinners, and its ingredients are 4
  skin-on thighs for 2 people — ~240g per person, ~48g of protein, not 75.5.
  It was single-handedly the only day in either Menu above 140g. This edits a
  Recipe that [Extract The Corpus](07-extract-the-corpus.md) verified as
  reproducing the source, so the source was wrong, not the extraction.

  After the correction, the twelve full days run **117–137.5g protein and
  1515–1760 kcal** — no day above 140g, every day under the ceiling.

### What this ticket did not do

**The four `null` slots in each Menu are a defect, not structure.** Both
rotations independently drop Friday pudding and run Saturday as breakfast-only,
which looked like a deliberate weekly shape. It is not: dropping meals is a
**Plan**-level act, and a Menu stays complete at 28 slots so there is something
to switch around. `CONTEXT.md` already said this and is correct as written.

Filling them needs the weekly protein-type layout, which `GOALS.md` under-
specifies — it covers 7 breakfasts but only **5 lunches, 6 dinners and no
puddings** for a 28-slot Menu. Split out as
[Complete The Weekly Layout](14-complete-the-weekly-layout.md).

### Domain model

`CONTEXT.md` gains **Band**, and its `Macros` entry now points at it. A Band
guides and does not gate — that is the part worth having written down.
