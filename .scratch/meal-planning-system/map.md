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

- [Mint The Pin Catalogue](issues/11-mint-the-pin-catalogue.md): **rules
  settled, writing split out.** `unit` is how the recipe measures it and `pack`
  is how it is sold — amending [How Ingredients Are
  Named](issues/04-how-ingredients-are-named.md), because the corpus writes
  150g, 240g and 300g of cannellini and whole cans would make those recipes
  lie. Every slug gets a Pin except `water`; near-duplicate slugs are left to
  Normalise Ingredient Units. `search_term` is the harvested product name
  verbatim. Unpinned means no row. Only 13 of 112 slugs disagree on unit, so
  the normalisation job is small.

- [Per-Slot Macro Bands](issues/06-per-slot-macro-bands.md): **four Bands, one
  per Slot, each a target plus a range — and they guide, they do not gate.** The
  daily goals were mis-stated: protein is a **floor** and kcal a **ceiling**, not
  a band and a target, which turns a corpus that failed its own goals 0/12 on
  calories into 12/12 without touching a Recipe. The four targets sum to ~132g /
  ~1685 kcal, because range-legal does not imply goal-compliant — a day can be
  built band-legal at 113g or 1880 kcal, so the check lives on the day, not the
  Recipe. Bands are per Slot only; breakfast's egg/sausage split (17–27 vs
  29–32, no overlap) is a note, not two Bands. Pudding's range is deliberately
  widened past its 4-recipe sample. Corrected the Moroccan chicken from 75.5g to
  48g — a corpus error, not an extraction one. `CONTEXT.md` gains **Band**.

- [Confirm And Write The Pins](issues/13-confirm-and-write-the-pins.md):
  **`PINS.md` written — 94 Pins, 18 absences, all 112 slugs reached.** 62 carry
  harvested line numbers, 7 are counter proteins, 25 are Staples with no product
  yet: **a Pin does not need a product**, which is what stops `salt` appearing on
  every shopping list as Unpinned. All six conflicts turned out to be switches
  over three dated orders, so **recency wins and the loser becomes an
  `alternate`** — except where explicit recipe text overrides it, as with the
  Puy lentils. Near-duplicate slugs Pin to the same line number rather than being
  collapsed. 38 Pins are Staples, `curry-powder` among them; `garlic`, `ginger`
  and `black-olives` were deliberately left off and fall through to absences.
  The minting procedure is now `Orders/HARVEST.md` steps 6-9.

- [Normalise Ingredient Units](issues/12-normalise-ingredient-units.md):
  **one rule, checkable** — an ingredient line's `unit` equals its Pin's, or the
  line has no `qty` and its Pin is a Staple. That second branch answers Extract
  The Corpus's "no way to say quantity unknown" for the 19 staple lines; the six
  non-staple blanks got estimates, because a list cannot add a blank. `water` is
  **deleted from the Recipes** rather than Pinned or exempted — unbuyable and
  unsummable, and every method already says "a splash". Five near-duplicate
  slugs merged and two kept, with **juice folded into fruit** at 20g = half a
  lemon, so a list can finally add lemons. Three Pin units looked wrong and were
  left alone; the Recipes moved, because the Pins were confirmed by hand. The
  ticket was scoped too small: it named 8 unit fixes as 13, one `or` as 13, and
  inherited two more jobs from resolved tickets. **`PINS.md` is now the only
  home of `staple`** — 87 Pins, 17 absences, and the Absences list *is* the
  Unpinned flag.

- [Complete The Weekly Layout](issues/14-complete-the-weekly-layout.md):
  **a Menu is 28 Slots, pudding nightly, and both Menus are now complete.**
  Measured, not preferred: strip the pudding and **0 of 10 corpus days reach the
  ~130g floor** where 5 of 10 do with it — pudding is the most protein-efficient
  Slot there is. **Fakeaway is a tag, not a protein type**, so `GOALS.md` was
  double-counting Friday's dinner; the unassigned dinner was always **Saturday**,
  and it stays **free**, chosen per Menu. Lunch becomes a floor — 7, tofu or
  chicken, at least 2 of each — because the 3-tofu/2-chicken ratio was never once
  followed and the two Menus lean opposite ways. Saturday is filled and the
  **Plan** removes it when you are out. Surfaced two tickets rather than
  absorbing them.

- [What The Four Skills Are](issues/08-what-the-four-skills-are.md): **four
  skills and one script**, seamed on re-runnability and on mechanical-versus-
  judgement. `bin/shopping-list.py` is the repo's only code, authorised here and
  nowhere else — the transform is plain addition plus a `ceil()`, measured at 39
  shoppable lines from Menu 1, and an agent summing 180 ingredient uses in prose
  will err silently. **Plan-the-week stays two skills** because the shopping
  section is regenerated whenever the Plan changes. Skills live in
  `.claude/skills/`; `Orders/HARVEST.md` does **not** move, because it is read
  on demand rather than invoked. `new-recipe` is the only writer to the pool, so
  `new-menu` **fails and names the gap** instead of minting. The harvest is step
  1 of planning — last week's order should serve this week. Hard-fail on a
  Recipe/Pin violation, fall back and flag on a missing `pack`. The script
  checks the mechanical, the skill **reports** the day sums and never blocks.
  Retired [The Query String Generator](issues/10-the-query-string-generator.md)'s
  original question — `search_term` was already stored at 44/44 coverage — and
  rewrote it as a verification.

- [How A Plan Records Bulk-Cook And
  Eat-Cold](issues/22-bulk-cook-and-eat-cold.md): **neither — no multiplier, no
  back-reference, no note.** The premise was false: a Recipe serves 2, two Slots
  need 4 portions, and buying twice gets 4 whether it is one pan or two — the
  script sums before it rounds to packs, so even the `ceil()` is identical. A
  Menu is 28 filled Slots, so **no portion exists that the grid is not already
  paying for**, confirmed with the user. Doubling is spelled **the same Recipe
  in both Slots**, which is the Recipe swap a Plan already has. Both Menus were
  **already doing it** — an adjacent-day repeat, always a lunch, never a dinner,
  three times over — and shopping correctly the whole time. **0 of 37 Recipes
  carry either tag**; they are kept against rule 2, at the price of a standing
  rule now in `VOCABULARY.md`: **`bulk-cook` and `eat-cold` have no consumer**,
  so nothing generating, planning or shopping may branch on them. Unblocks
  [The Shopping List Script](issues/17-the-shopping-list-script.md) and
  [Author The Plan-The-Week Skill](issues/20-author-plan-the-week.md).


## Not yet specified

<!-- Emptied by [What The Four Skills Are](issues/08-what-the-four-skills-are.md),
     07-08 September 2026. All four patches either graduated into tickets 17-22
     or were answered outright. Checked again on resolving [How A Plan Records
     Bulk-Cook And Eat-Cold](issues/22-bulk-cook-and-eat-cold.md), 08 September
     2026: still empty — that answer removed a representation rather than
     opening one. Refill as the frontier advances. -->

- **Nothing currently in the fog.** The four patches that stood here are gone:
  skill authoring graduated to tickets 18-21 and the script to 17; the shopping
  list's shape was settled inside
  [What The Four Skills Are](issues/08-what-the-four-skills-are.md); the basket
  review step turned out to need no automation to exist — it *is* the shopping
  section you read before pasting; and `bulk-cook`/`eat-cold` sharpened into
  [How A Plan Records Bulk-Cook And Eat-Cold](issues/22-bulk-cook-and-eat-cold.md)
  once the grid gained a consumer that parses it.

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
