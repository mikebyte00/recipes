# Meal Planning

A personal system for planning a household's weekly food: a pool of Recipes and
a weekly Plan built from them, yielding shopping output: a block that pastes
into Waitrose's Multi-search, plus counter lists for the butcher and
fishmonger. The problem being solved is time — assembling that order each week is
the expensive part, not deciding what to eat.

## Vocabulary

Read [CONTEXT.md](CONTEXT.md) before using the words Recipe, Slot, Plan,
Fakeaway, Macros or Store. Plan in particular means a specific thing here — one
real week, built Slot by Slot — and it drives the weekly workflow.

## This system is under construction

The route is charted as a wayfinder map at
[.scratch/meal-planning-system/map.md](.scratch/meal-planning-system/map.md),
with its open questions as tickets in the adjacent `issues/` directory.

**File formats and folder layout are not settled yet.** Read the map before
inventing a shape for anything — the question is likely already an open ticket,
and answering it in passing loses the decision. The original two-week corpus
lived in `Rotations/`; it was the input to the extraction, and `git show
0beccfa:Rotations/Week1.md` still reads it.

## There are exactly two pieces of code

Named, because the list is the rule:

- **`bin/shopping-list.py`** aggregates a Plan into its shopping section. Ruled
  in [What The Four Skills Are](.scratch/meal-planning-system/issues/08-what-the-four-skills-are.md).
- **`bin/browse.py`** generates `index.html`, the browse interface over Recipes,
  Plans and Orders. Ruled in
  [Browse The Pool](.scratch/meal-planning-system/issues/24-browse-the-pool.md).

A **third** `bin/` entry is a decision, not a convenience — raise it as a
ticket. Everything else is prose, because everything else is judgement.

`index.html` is generated and committed, and regenerating it is manual:
re-run `bin/browse.py` whenever a Recipe, Plan, Pin or Order changes.
`bin/browse.py --check` says whether the committed page has gone stale.

**Parity between the Recipes, `index.html` and GitHub Pages is vital.** The
page is served from the branch root at `mikebyte00.github.io/recipes`, so the
committed `index.html` *is* what the household reads on a phone in the kitchen.
A markdown change that stops there is invisible. Every edit to a Recipe, Plan,
Pin or Order therefore finishes the same way, and the change is not done
until it has:

1. `.venv/bin/python bin/browse.py` — regenerate the page.
2. `.venv/bin/python tests/test_browse.py` — 73 tests, including the redaction
   ones. Fourteen shell out to `node` — to run the page's theme boot script and
   its eaten-days count — and skip cleanly when it is absent. `test_reads_every_captured_order` fails on a
   checkout with no harvested `Orders/*.md`, which are gitignored — that is the
   environment, not the code.
3. `git commit` the source change **and** `index.html` in the same commit.
4. `git push` — Pages serves the pushed commit, so an unpushed commit is a
   stale page.

**Use `.venv/bin/python`, not bare `python3`.** The test suite is stdlib, but
`bin/browse.py` needs PyYAML and Homebrew's python refuses to install into
itself (PEP 668). The venv is gitignored and per-machine, so a fresh clone
builds it once:

```bash
python3 -m venv .venv && .venv/bin/pip install pyyaml
```

Committing a Recipe without its regenerated page is the failure mode this
guards against: `--check` then reports stale on someone else's unrelated run,
and the live page quietly disagrees with the repo.

**The page publishes a redacted view of `Orders/`**, which hold real personal
data. Read [Browse The Pool](.scratch/meal-planning-system/issues/24-browse-the-pool.md)
before touching that redaction, and run `.venv/bin/python tests/test_browse.py`
afterwards — those tests exist to catch a redaction that stops redacting.


## The bar for a Recipe

New Recipes match the Recipes already in `Recipes/`. That bar is low on purpose,
and it is the thing an agent is most likely to get wrong by trying to be
impressive:

- One to three appliances. Air fryer, skillet, rice cooker, Ninja Sizzle.
- Few ingredients — three to eight for breakfast, lunch and pudding; a dinner
  plates a protein, a grain and a green and runs 7–12, median 9. Measured
  across the pool in [ticket 18](.scratch/meal-planning-system/issues/18-author-new-recipe.md).
- Methods of three to six numbered steps.
- Whole foods, low sugar, protein-forward.

Read a handful of the existing meals before generating one. Elaborate cheffy
recipes fail this project even when they hit the macros.

## Standing constraints

These are settled. Treat a request that contradicts one as a question worth
raising rather than a spec to follow.

- **Serves 2**, always, project-wide. Recipes carry no serving count.
- **Protein and kcal only.** Carbohydrates and fat are deliberately untracked.
- **Macros are approximations.** Store them as bare numbers, so a Plan can sum
  them. Write `~` on every macro figure shown to the user — the numbers are
  estimates and the tilde is the honest signal.
- **Targets live in [GOALS.md](GOALS.md)**: the daily nutrient goals and the
  per-Slot Macro Bands. Anything generating a Recipe or a Plan reads it.
- **Shopping lists split by Store.** Waitrose is the bulk; eggs, chicken, steak
  and honey come from Soutars; fish from Dorset Meats. Only Waitrose is online.

## Waitrose

The project **generates search terms for the user to paste**, and — since
14 September 2026 — can also **fill the trolley directly by line number**,
following [Orders/BASKET.md](Orders/BASKET.md). It still **does not place
orders**: checkout, payment and slot booking are the user's, always, and
credentials are never entered.

Basket-filling works only because every pinned row already carries a line
number; it never searches. Unpinned items have no line number and stay with
Multi-search. Read
[.scratch/meal-planning-system/issues/01-can-claude-drive-waitrose.md](.scratch/meal-planning-system/issues/01-can-claude-drive-waitrose.md)
before proposing automation beyond that. `robots.txt` disallows the trolley,
search, order-history and lists paths. The user overruled it for the trolley,
product and order-history pages — their own session, their own basket, at their
own request — and that overrule covers **those surfaces and nothing else**.
Search stays off the table on relevance grounds regardless: it resolved
1 ingredient in 7. Multi-search deep links are a normal navigation the user
clicks, which is why they are fine.

**Harvesting orders is the one exception**, and it is read-only: capturing a
completed order's items and line numbers from the user's own signed-in session
follows [Orders/HARVEST.md](Orders/HARVEST.md). Read it before driving a
browser against Waitrose for any reason.
