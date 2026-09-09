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
- **Mobile-first**, light-only.
- `Plans/` is deliberately **out of scope**. A Plan is one week's mess; the
  interface is for the standing artifacts.

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

### Unresolved, and deliberately not fixed here

**`Orders/11-august.md`, `25-august.md` and `31-august.md` are tracked in git**,
order numbers, postcode, collection windows and Toiletries included. Redacting
`index.html` protects the *page*; it does nothing for the *repository*. If this
repo is made public to serve Pages from the branch root, the raw order files are
public with it — and they are in the history, so deleting them later does not
retract them.

There is **no git remote configured**, so nothing has been exposed.

Put to the user, who chose to **build the redaction and flag this rather than
rewrite history or strip the source files**. The resolutions available, for
whoever settles it:

- serve Pages from a **private** repo, which keeps the raw files unpublished;
- strip the source files and rewrite the history before any remote is added;
- move `Orders/*.md` out of the repo entirely.

**Do not add a remote and enable Pages until this is decided.**
