# Browse The Pool

Type: decision
Status: resolved
Blocked by: —

## Question

The repo now holds 41 Recipes, 2 Menus, 87 Pins and 3 captured orders, and every
one of them is markdown authored for a human to write and an agent to parse.
Nothing reads them back. Answering *which dinners clear 50g*, *which Menus use
this Recipe*, *what have we bought twice that still has no Pin* means grepping
across four directories and holding the join in your head.

Every fact needed to answer those is already in the files. What is missing is a
surface.

The obstacle is a standing rule. `CLAUDE.md` states the project authorises
**exactly one piece of code**, `bin/shopping-list.py`, and that a second `bin/`
entry is *"a decision, not a convenience — raise it as a ticket."* This is that
ticket.

Two things make it more than a convenience question. The repo is heading for
**GitHub Pages**, so whatever is built is published — and `Orders/*.md` are mode
600 and hold real personal data. And the four skills all *write*; nothing in the
project reads the corpus back as a whole, which is where drift hides.

## Answer

**Authorised, built and verified. `bin/browse.py` generates `index.html`, and
the one-code rule becomes two named entries.**

### The authorisation, and its limit

The one-code rule existed to keep the repo human-readable — prose for judgement,
code only where an agent would err silently at arithmetic. The user ruled that
**this HTML is intended to be the proper interface**, which is the rule's own
goal rather than an exception to it: a generated page that reads the markdown
back is the readability the rule was protecting.

`CLAUDE.md` now names **two** entries. This is **not** a general licence. A
third `bin/` entry is still a decision and still a ticket; the sentence that
says so is unchanged.

### Architecture

- **`bin/browse.py`** parses `Recipes/`, `Menus/`, `PINS.md`, `GOALS.md` and
  `Orders/`. PyYAML for frontmatter — already a dependency — and regex for the
  Order tables, which have no frontmatter.
- It emits **one self-contained `index.html` at the repo root**, every datum
  inlined as JSON. No server, no build step, no runtime fetch: `file://` CORS
  would block them, and Pages should not need a pipeline.
- **Committed** to git, so Pages can serve it from the branch root — which is
  why it is `index.html` and not `browse.html`.
- Regenerated **manually**. No CI workflow, no git hook. `bin/browse.py --check`
  fails if the committed page is stale, so the omission is detectable.
- **Mobile-first.** Originally **light-only**. **Amended on 16 September 2026**:
  the user asked for both themes and a toggle, and the cost turned out to be
  the theme block plus three new variables rather than any new machinery.

  The palette is **13 custom properties in two blocks** — one light, one dark —
  and `data-theme` is always written onto `<html>` by a boot script in `<head>`,
  so the cascade never consults `prefers-color-scheme` and neither block is
  duplicated. The boot script runs before first paint; without it the page
  flashes cream on its way to dark. It is wrapped in `try`/`catch` because
  `localStorage` throws in some privacy modes and on some `file://` origins,
  and a theme preference must never be able to stop the page rendering.

  Three variables existed only as hardcoded values before and had to be named
  to make the dark theme possible: `--on-accent` (white on the light accent,
  near-black on the lightened dark one — white on `#e09468` sits near 2:1),
  `--shade` and `--scrim`, whose warm-brown alphas were invisible on a dark
  ground.

  **The toggle has two states, not three.** The stored value *is* the override
  and its absence means "follow the system", so there is no separate Auto to
  explain, and a `change` listener keeps the system's casting vote while no
  choice is stored. Verified by running the shipped boot script against all
  seven cases — both stored values against both system preferences, neither
  stored against both, and `localStorage` throwing.

  The dark palette is a **warm near-black**, not a neutral grey: the light
  theme is cream paper and burnt sienna, and a cold dark would read as a
  different site. All 22 foreground/background pairs across both themes were
  measured against WCAG AA — **0 failures**, the tightest being `--under` on
  light paper at 4.41:1 against a 3.0 bar for a non-text band indicator.
- `Plans/` was originally **out of scope** — a Plan is one week's mess and the
  interface was for the standing artifacts. **Overruled on 16 September 2026**:
  the page is what the household reads on a phone in the kitchen, and the
  question it is asked most is *what am I cooking tonight, and where is that
  Recipe*. Only a Plan answers that. `Plans/` now has its own section, in the
  nav slot `Menus` used to hold.

  The original concern survives as a rule rather than an exclusion: **a Plan is
  never checked against the Weekly Layout**. A real week deviates on purpose —
  days away, Slots eaten out, a Recipe swapped — so `layout_violations` stays a
  Menu-only judgement, and a day with nothing cooked at home is not measured
  against the daily goals either. Reporting a night out as a nutritional
  failure is exactly the "one week's mess" noise this was meant to keep out.

  Menus keep their pages and their layout checking; they are simply no longer
  in the nav. A Recipe's **Used by** still links to them, which is what the
  orphan count depends on.

- The landing view was originally the **Recipe list**, and the nav read
  `Recipes · Plans · Past orders`. **Amended on 16 September 2026**: giving
  `Plans/` a section answered *what am I cooking tonight* in principle and left
  it three taps away in practice — open the page, tap Plans, tap the week,
  scroll to today. The nav is now `Today · Recipes · Plans · Orders` and the
  default route is `#today`.

  **`#today` holds no new data.** It resolves the week from `new Date()` in the
  reader's browser and looks up the Plan whose slug is that week's Monday, so
  the same committed `index.html` is correct on Thursday as on Monday. Baking
  the date in at generation time would make the page wrong by Tuesday, which is
  the same staleness trap `--check` exists for, with no `--check` to catch it.

  Today's day renders as the Plan's own day block, marked `.now`; the remaining
  six follow. When no Plan covers the current week the page says so and falls
  back to the latest Plan's full week **without** marking a day as today —
  labelling last week's Wednesday *Today* in a kitchen is worse than one more
  scroll. With no Plans at all, `#today` renders the Recipe list, so a fresh
  repo still has a front door.

  The rule from the `Plans/` amendment is unchanged and now matters more: a
  Plan is still never checked against the Weekly Layout, and `#today` reports a
  day with nothing cooked at home as *nothing cooked at home*, not as a
  nutritional failure.

### `tests/` — the repo's first tests, and why

`tests/test_browse.py`, **52 tests**, stdlib `unittest`, no new dependency and
no runner. Run with `python3 tests/test_browse.py`.

This is a new directory and therefore a shape decision, taken here rather than
in passing. The repo's precedent for verification is *run it against the real
corpus and record the numbers* (tickets 17–21), and that precedent is kept — the
last seven tests read the real files. But it is not sufficient here, for one
reason: **a redaction that silently stops redacting publishes personal data**,
and "I ran it and looked" does not survive the next edit. `bin/shopping-list.py`
still has no tests and needs none; its failure mode is a wrong shopping list.

`tests/` is not a `bin/` entry. It is not invoked, it produces nothing, and it
is not part of the workflow.

**Grown to 69 on 16 September 2026**, seven of them covering the theme boot
script. Those seven are the file's one departure from stdlib-only, and the
departure is bounded on purpose: the script decides, before first paint, what
the reader sees, and Python cannot reach it. They shell out to `node`, they
are `skipUnless(shutil.which("node"))` so a machine without it reports skips
rather than failures, and they lift the script **out of `TEMPLATE` rather than
restating it** — a test holding its own copy of the logic passes forever after
the real one breaks. Verified by mutation: inverting `saved === 'dark'` turns
four of the seven red, and reverting turns them green.

### Redaction, twice over

The published page omits **order numbers, the collection branch and postcode,
the collection date/time window, and the entire `Toiletries, Health & Beauty`
category**. It keeps the Household category, item names, sizes, quantities,
prices, totals, line numbers and the order date.

Two independent mechanisms, deliberately:

1. **Omission at parse time.** `parse_order()` never reads the preamble line
   into its result and never emits a redacted category. There is no later stage
   that *could* reintroduce them, because nothing downstream ever held them.
2. **`assert_no_pii()` refuses to write.** It derives the forbidden strings
   *from the raw order files themselves* — order number, time window, branch,
   postcode, and every item name and line number under a redacted heading — and
   raises rather than writing a page that contains any of them. Deriving from
   source means a fourth order file with a different branch is covered without
   anyone remembering to add it.

Verified independently of both, by grepping the generated `index.html` for every
PII string by hand: **0 hits** for all three order numbers, the collection
branch, the postcode, all five collection windows, both toiletries products and
both their line numbers. The strings themselves are not quoted here; the repo is
public, and naming them in the decision record would undo the redaction it
documents. The two apparent hits are the page's own notice of *what it
omits*, which is intended.

The page says so on its face rather than silently dropping rows.

### Computed, never read

Menu day totals and protein-type composition are **summed from the Recipes**,
not lifted from the prose table written into each Menu file. If the two
disagree, that drift is a bug and should be visible.

Measured on both Menus: **all 14 days agree exactly** with their written tables,
and both Menus are clean against the Weekly Layout with **0 days** missing the
~120g floor or the ~1800 kcal ceiling. Agreeing today is the point — the check
is worth having precisely because nothing enforces it.

### Search covers both vocabularies — including the shelf's

Free text is **case-insensitive substring, no fuzzy matching**, over the Recipe
title, its slug, ingredient display names, ingredient slugs, method text **and
the Pinned product name**.

That last one was a correction found by running it. The design said "display
names from `PINS.md`", but `display` is the *Recipe's* word — `Parmesan`,
`Pine nuts`. The word that disagrees lives on `search_term`: `Duchy Organic
Parmigiano Reggiano DOP`, `Waitrose Duchy Organic Pine Kernels`. Searching
`parmigiano` returned **nothing** until `search_term` joined the haystack, which
is the exact failure the dual-vocabulary requirement existed to prevent.
`Orders/HARVEST.md` exists because those two vocabularies disagree; a search
over only one of them is a search over the wrong one half the time.

### What it surfaces on day one

| | |
| --- | --- |
| Recipes | 41 |
| **Orphans — used by no Menu** | **4** |
| Menus | 2, both clean on the Weekly Layout |
| Distinct items bought across 3 orders | 84 |
| **Bought but not Pinned** | **28**, of which **4 bought more than once** |
| Pins | 87 |

The 4 orphans are the four Recipes written after both Menus were assembled —
the two yogurt pots, the jerk chicken and the sticky chilli orange chicken.
Nothing was wrong; nothing had ever said so.

The **4 items bought more than once with no Pin** are the pinning worklist, and
they were invisible before this page existed.

### Costs accepted

- **`index.html` is unreadable in a diff.** It is a 200KB JSON payload plus a
  template; a one-word Recipe edit rewrites a line thousands of characters long.
  Accepted, because the file is an artifact and its source is `bin/browse.py`
  plus the markdown. Review the inputs, not the output.
- **Regeneration is manual and therefore forgettable.** `--check` is the
  mitigation, not a fix. Automating it is a CI decision nobody has asked for.

### The repository risk, and how it was settled

**Settled 09 September 2026. The repo is public and Pages serves the page; the
order files were taken out of the repo and out of its history first.**

The risk as originally written: `Orders/*.md` are tracked, order numbers, branch,
postcode, collection windows and a personal-care category included. `browse.py`
redacts the *page*; it does nothing for the *repository*. Serving Pages from the
branch root publishes the repo alongside the page.

Three resolutions were offered — a private repo, strip and rewrite, or move
`Orders/` out entirely. The user chose to **publish publicly, with the order
files removed from the repo and purged from the history**, and judged the
order numbers and the postcode to be the data that actually matters. The
personal-care lines were scrubbed in the same pass regardless.

**The ticket's own statement of the risk was incomplete, and that is the lesson
here.** It named three files. A scan of every tracked path found the postcode
and real order numbers in **five**:

| Where | What |
|---|---|
| `Orders/{11,25,31}-august.md` | the captured orders themselves |
| `Orders/HARVEST.md` | a worked example built from a real order |
| `tests/test_browse.py` | a fixture using real values *on purpose*, to prove the guard catches them |
| `issues/24-browse-the-pool.md` | this file, quoting the strings while documenting their redaction |
| `issues/09-harvesting-past-orders.md` | an order number quoted as an example |

Two of those exist *because* of the redaction work: a test proving PII is caught
has to contain PII, and a decision record explaining what is hidden reaches for
the thing it hides. Redaction machinery grows its own copies of the secret. A
future audit should assume the same and grep, not read.

### What was done

1. `.gitignore` gains `Orders/*` with `HARVEST.md` and `history.md` allowlisted
   — a new order file is ignored by default, so tracking one has to be a
   deliberate act rather than a slip.
2. `git filter-repo` purged the three order files from all 30 commits and
   replaced the PII strings that remained in the history of the other four
   files. **Two passes were needed**: the first replaced full product names,
   and `PINS.md`'s prose used short forms. One pass looked clean by the tests
   and was not.
3. The order files stay on disk. **`bin/browse.py` is unchanged** — it reads the
   filesystem, not git — so the same page is generated from the same sources.
4. `tests/test_browse.py`'s fixture became synthetic. It caught an incomplete
   edit doing so: the toiletries product was changed in the fixture but not in
   the assertion handed to `assert_no_pii()`, and the suite went red. The 52
   tests earned their existence a second time.

Verified on the pushed branch, not just locally: `origin/main` carries no order
number, no postcode, no branch name, and no string shaped like either beyond the
synthetic replacements. The three order files appear in no commit.

**Nothing was ever pushed before the rewrite** — the GitHub repo was empty, zero
refs. This matters: GitHub keeps unreachable objects addressable by SHA after a
force-push, so a rewrite done *after* a first push leaves the originals
retrievable on their servers. Rewriting before the first push is the only
version of this that fully works. Anyone repeating it elsewhere should check
`git ls-remote` is empty before trusting it.

### What this costs, from here

- **A redaction failure is now an internet-facing failure.** It used to leak to
  a local file. `python3 tests/test_browse.py` before any push that touches
  `browse.py`, and treat a change near `assert_no_pii()` as load-bearing.
- **Publishing is manual and two-step**: `python3 bin/browse.py`, then commit
  and push. `--check` reports staleness, and a stale page is now a stale
  *public* page.
- **A fresh clone cannot regenerate the page.** The order files are not in it,
  so `browse.py` has nothing to read for the Orders section. `index.html` is
  committed, so the page survives; regenerating it needs the order files on
  disk. Accepted rather than solved.
