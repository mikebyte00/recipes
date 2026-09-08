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

**Authoring a skill ends by running it.** Parse its frontmatter as YAML before
calling it done — an unquoted `: ` in a `description` makes a skill silently
unloadable, and [Author The Shopping-List
Skill](issues/21-author-shopping-list.md) shipped that defect until it was
checked. Run every step of the skill too: that same ticket's splice command was
wrong in a way no amount of reading it would have shown.

**A diff is not a diagnosis.** When what you asked for and what came back
differ, the cause may be the tool, the data, or the human in between — and
reading the difference cannot tell you which. [The Query String
Generator](issues/10-the-query-string-generator.md) invented a search failure
mode out of two deviations that were both the user's own edits. Ask before
naming a cause, especially when the pattern is your own.

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


- [The Shopping List Script](issues/17-the-shopping-list-script.md):
  **`bin/shopping-list.py` is written and reproduces every regression number
  exactly** — Menu 1 gives 180 ingredient uses → 63 quantified Pins → 24 Staples
  dropped → **39 shoppable lines** (34 Waitrose, 3 Soutars, 2 Dorset Meats) →
  14 Unpinned, and **0 Recipe/Pin rule violations across all 37 Recipes**. Menu 2
  runs clean at 42 lines. Decided the one shape it needed: a Plan Slot that was
  not cooked holds the reserved value **`eaten-out`**, now in `VOCABULARY.md`
  under The Plan grid. Pack division splits on `unit in {g, ml}` — a countable
  container means one unit is one pack, a measured amount against a different
  measure is **flagged, never converted**. The script prints to stdout and the
  skill writes it into the Plan. Surfaced [Fix The Flagged
  Pins](issues/23-fix-the-flagged-pins.md). Unblocks [Author The Shopping-List
  Skill](issues/21-author-shopping-list.md).


- [Fix The Flagged Pins](issues/23-fix-the-flagged-pins.md): **all six fixed and
  `litre` retired from the pack vocabulary** — `bin/shopping-list.py` now emits
  **0 flags** on both Menus with every regression number from
  [The Shopping List Script](issues/17-the-shopping-list-script.md) unchanged.
  Measured first, and it changed the framing: all four flagged Pins are
  single-sited and tiny (bread 9 slices, celery 100g, spring onions 30g, oat milk
  60g), so **no value here is load-bearing at a rounding boundary** — which is
  what made hand estimates acceptable at all. `oat-milk` moved to `ml` and the
  Recipe with it, retiring a one-off unit rather than teaching the script a
  conversion. `sourdough`'s `pack: 12 slices` is knowingly a **yield in a field
  that means pack size**, taken because the honest alternative re-flags the row.
  The two mayos were fixed rather than left: latent, and free to fix because no
  `qty` exists to migrate.


- [Author The Shopping-List Skill](issues/21-author-shopping-list.md):
  **written, and every step run before it was called done** —
  `.claude/skills/shopping-list/SKILL.md`, the repo's first skill.
  **Model-invoked**, because it is the one you reach for mid-week in a session
  about something else, which also leaves [Author
  Plan-The-Week](issues/20-author-plan-the-week.md) free to chain or hand off.
  Authoring forced three decisions: **`## Shopping` is a Plan's last section**
  (now in `VOCABULARY.md`, so regeneration is one deterministic replace);
  the section reaches the file **verbatim by construction**, because the splice
  re-runs the script rather than transcribing it; and a flag **asks for the pack
  size** rather than estimating it. Verified on a throwaway Plan: idempotent
  across three runs from both starting states, a hard failure leaves the Plan
  byte-identical, and **`eaten-out` works in a Plan** — never exercised outside a
  Menu before — taking Menu 1 from 39 lines to 37. Running it caught two defects
  invisible on the page, one of them a `description` that **failed to parse as
  YAML**; the lesson is now a standing line in Notes.


- [Author The Plan-The-Week Skill](issues/20-author-plan-the-week.md):
  **written, and every step run before it was called done** —
  `.claude/skills/plan-the-week/SKILL.md`, six steps. **Model-invoked**, because
  the cost of it not firing is not a retype but a Plan improvised by hand
  against a grid the script treats as fatal when short. It **chains** into
  `shopping-list`, the choice [Author The Shopping-List
  Skill](issues/21-author-shopping-list.md) deliberately left open: the
  re-runnability seam is an argument about the *second* run and says nothing
  against the first, and a Plan with no shopping section is a half-done job.
  The harvest stays step 1 but is **offered**, since a no-op harvest is free
  only once the browser is open — skipping it merely routes this week's new
  ingredients through **Unpinned**, which is the designed path anyway. The grid
  is lifted by `awk`, **verbatim by construction**, as ticket 21 did for the
  shopping section. **`menu:` is exercised for the first time** — mandated by
  [Where Everything Lives](issues/05-where-everything-lives.md), read by the
  script since it was written, and never carried by any file until now. Running
  step 5 caught what reading it could not: a day with `eaten-out` Slots reported
  UNDER the protein floor, a **false alarm** that would have trained the user to
  ignore the report, so such a day is now reported and **not judged**. The day
  sum is a heredoc importing `bin/shopping-list.py`, **not a second `bin/`
  entry**. Verified end to end on a throwaway Plan: 28 Slots copied, 39 lines,
  0 flags, idempotent, week notes surviving above `## Shopping`. Also corrected
  a number the map itself was carrying — [Raise The Weak
  Days](issues/16-raise-the-weak-days.md) is **six** short days, not five; its
  table always said six and only its prose said five.


- [Author The New-Recipe Skill](issues/18-author-new-recipe.md): **written,
  and every step run before it was called done** —
  `.claude/skills/new-recipe/SKILL.md`, five steps. **Model-invoked**, for the
  reason tickets 20 and 21 both give: not firing means a Recipe freelanced into
  the pool against a remembered bar. Model-invocation is **not** a licence to
  chain — the skill states that writing to the pool is the **user's decision**,
  keeping [What The Four Skills Are](issues/08-what-the-four-skills-are.md)'s
  "`new-menu` names the gap and stops" rule where the caller cannot lose it.
  The lever for holding the bar is **numbers, not adjectives**: step 2 makes the
  agent read three neighbours in the same slot and protein and *state their
  ingredient, appliance and step counts back*, and a measured per-slot table
  gives a draft something to land inside. **Measuring found a false premise
  again** — `CLAUDE.md`'s "three to six ingredients" holds for breakfast, lunch
  and pudding but **not for dinner**, which runs 7–12 with a median of 9; 12 of
  the 37 Recipes sit outside the stated bar. Two heredocs import
  `bin/shopping-list.py` and reuse its loaders, **no second `bin/` entry**: a
  Pin probe run *before* drafting, so units never pass through the agent, and a
  step-5 check that **collects every failure** rather than raising on the first,
  which is what `check_rule` alone does — it hid all vocabulary errors behind a
  traceback until a deliberately bad file exposed it. Verified with a full
  dry-run pudding, checked by the step-5 script **extracted from the SKILL.md**,
  exercising all three ingredient shapes; the draft was **deleted, not added to
  the pool**.


- [Author The New-Menu Skill](issues/19-author-new-menu.md): **written, and
  every step run before it was called done** — `.claude/skills/new-menu/SKILL.md`,
  five steps. **Model-invoked**, same reasoning as the other three, but it is
  the one skill of the four that **never chains anywhere**: a Menu is a
  standing artifact `plan-the-week` reads on demand, not a pipeline stage.
  **It never calls `new-recipe`** — a gap the pool cannot fill stops the skill
  and names the exact Slot and constraint, handing the grow-the-pool decision
  to the user rather than absorbing it. The seams collapse `GOALS.md`'s Weekly
  Layout into one table: six of seven dinners fixed by day, breakfast a 3/4
  split, lunch a **floor** of 2 tofu / 2 chicken (not a ratio), Saturday free.
  A step-2 probe groups the pool by `(slot, protein)` with macros so a fill is
  chosen from real numbers; a step-5 check reuses `load_grid`, `load_recipes`
  and `check_rule` from `bin/shopping-list.py` **unmodified** — a Menu's
  `days:` block is exactly the shape a Plan's grid is — **no second `bin/`
  entry**. Verified with a full dry-run Menu 3 assembled from the real pool:
  clean on completeness, resolution and the Recipe/Pin rule, correctly reported
  three days under the ~130g floor without blocking, and a second run against a
  deliberately bad slug confirmed the hard-fail path. The draft was **deleted,
  not added to `Menus/`**. **This completes the four-skill set** first sketched
  in [What The Four Skills Are](issues/08-what-the-four-skills-are.md).


- [The Query String Generator](issues/10-the-query-string-generator.md):
  **the terms resolve — 34 of 34, first hit.** Pasted into Multi-search against
  a real Plan, every harvested `search_term` returned its intended product,
  against [Can Claude Drive Waitrose](issues/01-can-claude-drive-waitrose.md)'s
  1-in-7 for naive recipe words. **The last untested assumption in the design
  is now tested, and it held.** The real gap is **quantity**: Multi-search
  carries no count syntax and adds 1 of everything, so 13 of 34 lines needed a
  second pass by hand — a fact buried in a `Buy` column read while shopping
  rather than while pasting. `bin/shopping-list.py` now renders a **counts
  block** under the paste block; `divide()` already computed the number and
  `build()` was throwing it away. The fallback for a missed term stays
  **untested and unhurried**, since nothing missed and every row already carries
  its `line_number`. **A correction is recorded in the ticket**: the first read
  of this run reported two silent mismatches and generalised them into a
  failure mode, and all of it was wrong — both deviations were the user's own
  edits. A basket differs from a list for many reasons and search relevance is
  only one; a diff cannot tell a bad match from a human edit, only asking can.


## Not yet specified

<!-- Emptied by [What The Four Skills Are](issues/08-what-the-four-skills-are.md),
     07-08 September 2026. All four patches either graduated into tickets 17-22
     or were answered outright. Checked again on resolving [How A Plan Records
     Bulk-Cook And Eat-Cold](issues/22-bulk-cook-and-eat-cold.md), 08 September
     2026: still empty — that answer removed a representation rather than
     opening one. [The Shopping List Script](issues/17-the-shopping-list-script.md)
     added nothing here either; its one finding was sharp enough to ticket
     directly. Checked a third time on resolving [Fix The Flagged
     Pins](issues/23-fix-the-flagged-pins.md), 08 September 2026: still empty —
     that ticket closed a defect class outright rather than opening a question,
     and a whole-catalogue scan confirmed no successor defect is hiding.
     Checked a fourth time on resolving [Author The Plan-The-Week
     Skill](issues/20-author-plan-the-week.md), 08 September 2026: still empty.
     That ticket closed the two open choices it inherited (chain, and
     model-invoke) rather than opening any, and its one surprise -- the
     eaten-out false alarm -- was fixed in the skill on the spot.
     Checked a fifth time on resolving [The Query String
     Generator](issues/10-the-query-string-generator.md), 08 September 2026:
     still empty. The one question it leaves open -- what to do about a
     `search_term` that misses -- is deliberately parked in that ticket rather
     than promoted here, because no miss has ever been observed to characterise.
     Checked a sixth time on resolving [Author The New-Recipe
     Skill](issues/18-author-new-recipe.md), 08 September 2026: still empty.
     Measuring the corpus for its bar table surfaced one discrepancy -- that
     `CLAUDE.md`'s "three to six ingredients" is false of dinners -- but that is
     a correction to the user's own instruction file, raised with them rather
     than promoted here. It opens no design question.
     Checked a seventh time on resolving [Author The New-Menu
     Skill](issues/19-author-new-menu.md), 08 September 2026: still empty. This
     ticket closed the four-skill set outright rather than opening a question.
     Refill as the frontier advances. -->

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
