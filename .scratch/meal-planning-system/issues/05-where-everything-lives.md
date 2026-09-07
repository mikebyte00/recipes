# Where Everything Lives

Type: grilling
Status: resolved
Blocked by: 02

## Question

What is the folder structure of this repo?

Four kinds of thing need a home: Recipes, Menus, Plans, and the archive of Plans
already eaten. `Rotations/` currently holds two Menus as whole-week markdown
documents, which the extraction will dissolve.

Grill on:

- Are Recipes in one flat directory, or foldered by slot or protein type? Flat
  scales badly for a human browsing; foldered fights Recipes that serve two
  slots.
- Do Menus stay human-readable prose documents, or become lists of Recipe
  references? The current files are lovely to read and terrible to query.
- Where do Plans live, and how is an archived Plan distinguished from the
  current week's?
- Does `GOALS.md` stay at the root as the single tuning file it is today?

## Comments

**Obligation inherited from [The Tag Vocabulary](03-the-tag-vocabulary.md).**
That ticket settled the *content* of five closed vocabularies — `slot`,
`protein`, `effort`, `appliances`, `tags` — and deliberately did **not** decide
where they are written down, because file placement is this ticket's call.

Its `## Answer` is the source of truth until then. This ticket must give the
vocabulary a home file, and answer: is it one file or one per vocabulary, does
it sit beside `GOALS.md` at the root, and is it the same artifact the Pin
catalogue lives in?

## Answer

**Root-level directories, flat Recipes, structured Menus and Plans.**

```
CLAUDE.md  CONTEXT.md  GOALS.md  VOCABULARY.md  PINS.md
Recipes/   <slug>.md x37
Menus/     menu-1.md  menu-2.md
Plans/     2026-09-07.md ...
Orders/    HARVEST.md  history.md  11-august.md  25-august.md  31-august.md
```

### No container directory

The repo *is* the data plus three instruction files. There is no source code to
separate data from, so a `data/` wrapper would buy separation from nothing and
add a segment to every path a skill writes.

`Orders/HARVEST.md` is **ratified where it sits**, on the co-location argument:
a procedure belongs beside its output. `CLAUDE.md`'s pointer to it stands.

### Recipes are flat

`Recipes/<slug>.md`, one directory, no sub-folders.

The ticket's stated objection to foldering — that it "fights Recipes that serve
two slots" — is **dead**: [The Tag Vocabulary](03-the-tag-vocabulary.md)
verified that no recipe in the corpus serves two slots, and made `slot` a
single-valued field.

The real objection is stronger. `slot` and `protein` are **already frontmatter
fields**, so foldering by either duplicates a field into the path — the same
two-sources-of-truth failure that
[What A Recipe File Looks Like](02-what-a-recipe-file-looks-like.md) cited when
it refused an `id` field alongside the filename. Re-slotting would become a
move, and the field and the folder could then disagree.

37 files is browsable. Filename-as-identity stays clean: a Menu references
`zero-prep-sausage-chickpea-crisp-hash` with no path to get wrong. **If
browsing ever hurts, the fix is a generated index, not a directory tree** —
deliberately deferred until it does.

### Menus are structured references

`Menus/menu-N.md`. Frontmatter naming a Recipe slug per day per slot. No prose.

A Menu exists to be copied into a Plan and have a shopping list derived from
it — that is a query, every time. `Rotations/Week1.md` reads well only because
it **inlines all 28 recipe bodies**, and duplicating recipes into every Menu is
exactly what the extraction exists to stop.

**Accepted cost:** you can no longer read a week end-to-end in one file.
Readability returns as a rendered view generated on demand, never as the
storage format.

**Named positionally on purpose.** `menu-1`, `menu-2` — these two are arbitrary
rotations with no distinguishing character, and inventing descriptive names for
them would be fiction. Rename when one earns it; the cost is low because Menus
are referenced only by Plans, unlike Recipe slugs which are referenced by every
Menu.

### Plans are date-named, and there is no archive

`Plans/YYYY-MM-DD.md`, named for the week's Monday.

**A Plan is archived by continuing to exist.** "Current" is the one whose date
covers today. A separate `Archive/` directory would require a move step, and an
un-moved Plan would be silently absent from the variety measurement — a manual
step that corrupts data when skipped is worse than no step at all. ISO dates
sort correctly for free.

**A Plan stores the full resolved grid, plus a `menu:` field naming its
source.** Not a diff against that Menu: a diff breaks the moment the source
Menu is edited, silently changing what a three-month-old Plan appears to say —
and variety is measured over exactly those old Plans. A Plan must stay true to
the week actually eaten, independent of what its template has become since.

The `menu:` pointer keeps provenance without creating that dependency.
Deviations are marked in place — a slot may say "eaten out" instead of naming a
Recipe, which the current corpus cannot express at all.

### Shopping output is a section of the Plan

Regenerated on demand, overwritten in place. Not a sibling file: that doubles
what can go stale and orphans itself when a Plan is removed.

Not "never stored" either, despite being derived data — you need it on your
phone at the butcher's counter, and "run the tool again" is a bad answer while
standing in a shop.

**This closes a loop worth naming: the durable record of what was actually
bought already exists as `Orders/`, filled by the harvest.** So the shopping
section carries no archival duty. It is a working document for one week.

### Vocabulary and Pins are separate files, both at root

`VOCABULARY.md` and `PINS.md`.

They look alike — both lookup tables — but change on completely different
cadences. The vocabulary is a dozen lines that move when a *decision* moves;
the Pin catalogue is ~90 entries that move every time you shop. Merging them
means every harvest rewrites the file defining the schema.

Neither belongs inside `GOALS.md`: that holds targets, these hold schema and
bindings, and a generator reads them for different reasons.

**`VOCABULARY.md` is written as part of this resolution**, discharging the
obligation left by [The Tag Vocabulary](03-the-tag-vocabulary.md). `PINS.md` is
declared but **not** written — its content depends on canonical-ingredient
matching, open on
[Harvesting Past Orders](09-harvesting-past-orders.md).

### `Rotations/` survives until the extraction is verified

Then it is deleted, and **that deletion is an explicit step in
[Extract The Corpus](07-extract-the-corpus.md)**.

Deleting early loses the only source if the extraction is wrong. Leaving it
forever gives the repo a third source of truth for every recipe — which is how
the ganache discrepancy survived unnoticed. An explicit step is what stops it
becoming permanent by default.
