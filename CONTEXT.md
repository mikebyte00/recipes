# Context

The glossary for this project. Terms only — no implementation detail, no specs.

## Recipe

A single dish, scaled to a fixed number of servings, carrying its method and its
per-serving protein and kcal. The unit that lives in the pool and gets reused
across many [Menus](#menu).

## Slot

A position in a day that a [Recipe](#recipe) fills: breakfast, lunch, dinner,
pudding. Macro targets are expressed per slot, not only per day, because the
existing corpus already clusters tightly by slot.

## Menu

A **complete** seven-day rotation: every day, every slot, filled with a
[Recipe](#recipe). Never partial. Menus are reusable and go into rotation —
`Menus/menu-1.md` and `Menus/menu-2.md` are the first two.

A Menu is a template. It is not tied to any particular calendar week.

## Plan

A [Menu](#menu) selected for one specific week, then edited: days removed,
[Recipes](#recipe) swapped, meals eaten out. A Plan is where deviation from the
template is recorded.

**The shopping list is generated from a Plan, never from a Menu.** This is the
distinction that makes the weekly workflow tractable: the Menu stays clean and
reusable, the Plan absorbs the mess of a real week.

## Fakeaway

A [Recipe](#recipe) tag: a restaurant-style dish cooked at home, intended for
weekend slots. The Fakeaway Peri-Peri Chicken Burger is the existing example —
recorded as `'Nandos'` in the old spreadsheet, which was shorthand for the
recipe, not a note about eating out.

## Macros

Protein and kcal. Deliberately **not** carbohydrates or fat: the recipes are
whole-food and low-sugar, so those two numbers are the ones that carry
information. Targets are a per-[Slot](#slot) [Band](#band) plus daily goals.

## Band

The macro target for one [Slot](#slot): a protein and kcal figure to aim at,
plus the range either side that is acceptable. Four Bands, one per Slot, and
they live in [GOALS.md](GOALS.md) next to the daily goals.

A Band **guides**, it does not gate. Nothing is rejected for falling outside
one; the goals are checked by summing a day, not by policing a [Recipe](#recipe).
The four targets are chosen to sum to a day that clears those goals.

## Pin

A canonical ingredient bound to a specific purchasable product — one you have
vetted with your own money. A Pin is what turns "cannellini beans" into a thing
that can be added to a basket without guessing.

A past order is evidence for a Pin, not the only kind: the counter proteins and
the store-cupboard staples are vetted the same way and written by hand.

Pins are **stored in this repo**, not re-derived each week: a Pin is a decision,
and decisions belong somewhere you can see and correct them. Past orders are how
Pins get created, not where they live. A Pin holds only what was decided;
anything countable — how often something was bought, and when — stays countable
from the orders themselves.

A Pin also **declares the one unit its ingredient must be written in**, and
Recipes comply. That turns shopping-list aggregation into plain addition, and
makes a disagreeing Recipe a detectable error rather than a silent miscount.

## Staple

A [Pin](#pin) flagged as a store-cupboard item: salt, oil, spices, vanilla
extract, truffle oil. Recipes call for it, the weekly shopping list leaves it
out. This is what stops 5g of truffle oil appearing on a list every week.

## Unpinned

An ingredient a [Recipe](#recipe) needs that has no [Pin](#pin) yet. Unpinned
ingredients are **flagged, never guessed** — they are skipped by basket
automation and listed for you to add by hand.

Adding one by hand puts it in your order history, where the next harvest turns
it into a Pin. The manual work feeds the system rather than repeating.

## Protein Type

The single protein a [Recipe](#recipe) is built around, drawn from a closed
list. It is the axis `GOALS.md` plans against ("3x Tofu Lunch"), which is why
it is one value and not a set: a dish may contain chicken and halloumi, or beef
and parmesan, but only one of them is the protein being counted.

Never inferred from a Recipe's title — at least one Recipe in the corpus is
named for a bean and built on chicken.

## Tag

An optional capability of a [Recipe](#recipe), drawn from a closed list —
[Fakeaway](#fakeaway) is one. Tags record what a Recipe *can* do, never what a
given week did with it: whether you actually cooked a double batch, or actually
ate it cold, is a fact about a [Plan](#plan).

A tag that restates a field is a liability, not a convenience, and is rejected
on those grounds.

## Appliance

A piece of kit a [Recipe](#recipe) needs, drawn from a closed list. A Recipe
names one to three. The count is a real constraint later — a three-appliance
dinner is not a weeknight dinner.

## Effort

How complicated a [Recipe](#recipe) looks to cook, as low, medium or high.
Generated when the Recipe is written and then stored, not recomputed: a value
that changed between readings could not be planned against.

It reflects pans and parallelism as much as ingredient count — a nine-ingredient
dish cooked in one skillet is easier than an eight-ingredient dish spread across
three appliances.

## Store

Where an ingredient is bought. The existing shopping lists route across three:
Waitrose (the bulk), Soutars (eggs, chicken, steak, honey) and Dorset Meats
(fish). A shopping list is therefore split by Store, not flat.
