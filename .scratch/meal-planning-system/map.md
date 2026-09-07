# Map: The Meal Planning System

Label: `wayfinder:map`

## Destination

A working meal-planning system in this repo: the existing meals extracted into a
tagged Recipe pool, `GOALS.md` driving generation, and four skills — new Recipe,
new Menu, weekly Plan, and a shopping output that pastes straight into
Waitrose's Multi-search — proven by using them to plan and shop a real week.

The shopping output is the payoff and the hard part: turning canonical
ingredient names into search terms that actually find the right product.

## Notes

**Domain**: weekly meal planning for a household of two. Vocabulary lives in
[CONTEXT.md](../../CONTEXT.md) — read it before using any of these terms.

**Execution is in scope.** This map overrides wayfinder's plan-only default:
tickets here may build, not merely decide. The corpus already exists, so a spec
handed off to a separate effort would be ceremony.

**Skills every session should consult**: `domain-modeling` and `grilling` by
default. `writing-for-agents` when authoring any of the four skills.
`prototype` for file-shape questions. `research` for anything about Waitrose.

**Standing preferences for this effort**:

- Serves 2, fixed, project-wide constant. Not a per-Recipe field.
- Protein and kcal only. Carbohydrates and fat are out of scope.
- A Menu is always complete; a Plan is where a real week's deviation lives.
  Shopping lists derive from Plans.
- Plans are archived. Variety is measured against weeks actually eaten.
- Recipes are simple: one to three pans, short numbered methods, few
  ingredients. The existing 37 meals define that bar — match them.

## Decisions so far

- [What The Destination Is](map.md): build the working system, not a spec to
  hand off; Waitrose automation included, gated behind research.
- [How Variety Is Measured](map.md): against archived Plans — weeks actually
  eaten — which makes archiving mandatory.
- [Which Macros Count](map.md): protein and kcal only; daily targets now in
  `GOALS.md` at 130–140g protein and ~1800 kcal.
- [How Ingredients Bind To Products](issues/04-how-ingredients-are-named.md):
  a **Pin** stored in the repo, carrying pack size and a staple flag; Unpinned
  ingredients are flagged for manual adding, never guessed. Retires the pantry
  staples question.

- [Can Claude Drive Waitrose](issues/01-can-claude-drive-waitrose.md):
  **semi-automation only.** Search relevance is the blocker, not bot
  protection — 1 of 7 ingredients resolved cleanly, and wrong matches surface
  silently. Waitrose's first-party **Multi-search** gives the project its
  semi-automation surface for free. Product line numbers are stable and good.
  Order history and trolley paths are `Disallow`ed in `robots.txt`.

- [What A Recipe File Looks Like](issues/02-what-a-recipe-file-looks-like.md):
  **structured frontmatter, prose method.** Ingredients carry a canonical
  `ingredient:` key resolving to a Pin; identity is the filename; recipes list
  staples and the shopping list filters them. The ganache's two sizes were an
  error, not a feature — standard size wins.

- [How Ingredients Are Named](issues/04-how-ingredients-are-named.md): a
  **single Pin catalogue**, each Pin declaring the one unit its recipes must
  use — checked, not assumed. Lists quantify in Pin units as the original CSV
  did. No `or` in recipes; substitution lives on `alternates`.

- [The Tag Vocabulary](issues/03-the-tag-vocabulary.md): **five closed
  vocabularies, four of them fields** — `slot`, `protein`, `effort`,
  `appliances`, `tags: [fakeaway, bulk-cook, eat-cold]`. Tags are capability,
  never intent. `unhealthy`, `quick`, `side-dish` and `vege` rejected;
  `effort` (Claude-generated, stored once) supersedes `quick`. Pulled
  `appliances` in on finding 14 spellings for 8 appliances.

- [Where Everything Lives](issues/05-where-everything-lives.md): **root-level
  directories, no container.** `Recipes/` flat (foldering would duplicate the
  `slot` and `protein` fields into the path); `Menus/` structured references,
  no prose; `Plans/YYYY-MM-DD.md` with no separate archive — a Plan is
  archived by existing, and stores its full resolved grid rather than a diff.
  Shopping output is a regenerated section of the Plan. `VOCABULARY.md`
  written; `PINS.md` declared. `Rotations/` deleted once the extraction
  verified — it has, and it is.

- [Extract The Corpus](issues/07-extract-the-corpus.md): **done** — 37 Recipes
  and 2 Menus, every vocabulary value legal, every macro reproducing the
  corpus, no orphans. `Rotations/` deleted. Split first: unit normalisation
  needed a Pin catalogue that did not exist. Five format holes recorded; the
  two that needed a ruling got one — `protein` is omitted on a pudding, and
  the mandated `~` is a rendering rule, not a storage format.

- [Harvesting Past Orders](issues/09-harvesting-past-orders.md): **a harvest
  proposes, a human confirms, nothing is minted silently.** Matching is
  slug-driven, so the household shop never needs filtering; naive string
  matching scores 43 hits against 69 misses with ~10 of the hits wrong, and the
  wrong ones score *high*, which rules out any confidence threshold. Review
  happens in `PINS.md` itself via `confirmed`, so there is one file. A harvest
  runs inside weekly planning; it proposes changes to existing Pins and never
  overwrites; a losing conflict becomes an `alternate`. Pins hold decisions
  only, and line numbers revalidate lazily against the week's Plan.

## Not yet specified

- **Authoring each of the four skills.** Their contracts depend on the file
  formats and folder layout, so the writing can't be specified until those
  land. Expect one ticket per skill, possibly more for the Waitrose one.
- **How a shopping list is represented.** Its *location* is settled — a
  regenerated section inside the Plan. The shape is not: it must split by
  Store, quantify in Pin units, filter Staples, and flag Unpinned items, and
  that depends on how ingredients get canonicalised.
- **The basket review step.** If Waitrose automation works, there has to be a
  moment where you see what it chose before anything is ordered. What that
  looks like depends on what the research finds.
- **How a Plan records acting on `bulk-cook` and `eat-cold`.** The Recipe tags
  are capability only, settled in [The Tag Vocabulary](issues/03-the-tag-vocabulary.md).
  But a week that actually doubles a batch has to get doubled quantities onto
  the shopping list, and a meal eaten cold on Tuesday was cooked on Monday.
  That representation is a Plan concern and isn't sharp enough to ticket yet.

## Out of scope

- Carbohydrate and fat tracking. Ruled out in charting: it means re-estimating
  37 existing meals from AI guesses, for numbers the whole-food, low-sugar
  corpus doesn't need.
- Scaling recipes to serving counts other than 2. Bulk-cooking is handled as a
  Recipe tag, by cooking a dish twice, not by a scaling engine.
- Nutrition-database-grade macro accuracy. The `~` in every existing figure is
  honest and stays.
- **Driving the Waitrose basket — parked, not abandoned.**
  [Can Claude Drive Waitrose](issues/01-can-claude-drive-waitrose.md) found
  search too unreliable to trust unattended, guest add-to-trolley silently
  failing, and `robots.txt` disallowing the trolley path. String generation is
  the deliberate middle ground: it feeds Waitrose's own Multi-search via
  [The Query String Generator](issues/10-the-query-string-generator.md).

  Revisit as a **fresh effort**, not a resumption of this map, and only if
  something changes that fixes the underlying problem — a sanctioned API, or a
  Pin catalogue mature enough that search is bypassed entirely by line number.
  Good Pins are the prerequisite either way, so this map builds toward it
  without depending on it.
- Automating Soutars and Dorset Meats. Only Waitrose has an online basket;
  those two stay a printed list you take to the counter.
