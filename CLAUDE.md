# Meal Planning

A personal system for planning a household's weekly food: a pool of Recipes, a
set of reusable Menus, and a weekly Plan that yields shopping output: a block
that pastes into Waitrose's Multi-search, plus counter lists for the butcher and
fishmonger. The problem being solved is time — assembling that order each week is
the expensive part, not deciding what to eat.

## Vocabulary

Read [CONTEXT.md](CONTEXT.md) before using the words Recipe, Slot, Menu, Plan,
Fakeaway, Macros or Store. Menu and Plan in particular mean specific, different
things here, and the distinction drives the weekly workflow.

## This system is under construction

The route is charted as a wayfinder map at
[.scratch/meal-planning-system/map.md](.scratch/meal-planning-system/map.md),
with its open questions as tickets in the adjacent `issues/` directory.

**File formats and folder layout are not settled yet.** Read the map before
inventing a shape for anything — the question is likely already an open ticket,
and answering it in passing loses the decision. `Rotations/Week1.md` and
`Rotations/Week2.md` are the original two-week corpus; they are the input to the
extraction, not the target structure.

## The bar for a Recipe

New Recipes match the existing 37. That bar is low on purpose, and it is the
thing an agent is most likely to get wrong by trying to be impressive:

- One to three appliances. Air fryer, skillet, rice cooker, Ninja Sizzle.
- Few ingredients — often three to six.
- Methods of three to six numbered steps.
- Whole foods, low sugar, protein-forward.

Read a handful of the existing meals before generating one. Elaborate cheffy
recipes fail this project even when they hit the macros.

## Standing constraints

These are settled. Treat a request that contradicts one as a question worth
raising rather than a spec to follow.

- **Serves 2**, always, project-wide. Recipes carry no serving count.
- **Protein and kcal only.** Carbohydrates and fat are deliberately untracked.
- **Macros are approximations.** Every figure carries `~`. Keep it — the numbers
  are estimates and the tilde is the honest signal.
- **Targets live in [GOALS.md](GOALS.md)**: the weekly protein-type layout and
  the daily nutrient goals. Anything generating a Recipe or a Menu reads it.
- **Shopping lists split by Store.** Waitrose is the bulk; eggs, chicken, steak
  and honey come from Soutars; fish from Dorset Meats. Only Waitrose is online.

## Waitrose

The project **generates search terms for the user to paste**; it does not drive
the basket and does not place orders. That is a deliberate decision backed by
research, not a gap waiting to be filled — see
[.scratch/meal-planning-system/issues/01-can-claude-drive-waitrose.md](.scratch/meal-planning-system/issues/01-can-claude-drive-waitrose.md)
before proposing automation here. `robots.txt` disallows the trolley, search,
order-history and lists paths; Multi-search deep links are a normal navigation
the user clicks, which is why they are fine.

**Harvesting orders is the one exception**, and it is read-only: capturing a
completed order's items and line numbers from the user's own signed-in session
follows [Orders/HARVEST.md](Orders/HARVEST.md). Read it before driving a
browser against Waitrose for any reason.
