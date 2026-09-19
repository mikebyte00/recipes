# Retire Menus

Type: decision
Status: resolved
Blocked by: —

## Question

Weekly planning now happens entirely through the browse page's **Plan mode**:
clicking through the 28 Slots and pasting the resulting grid into
`plan-the-week`, in place of a copied Menu grid. The user confirmed Plan mode
has **fully replaced** Menus for real weekly planning.

That leaves `Menus/` and the `new-menu` skill as a second, unused way to answer
a question Plan mode already answers — and it leaves `GOALS.md`'s Weekly Layout
gating nothing. Checking the code paths: `layout_violations()` was only ever
called against a Menu in `bin/browse.py`, and `new-menu` was the only skill
reading the Weekly Layout to generate one. `plan-the-week` and a real
`Plans/*.md` never checked it. The Weekly Layout had already stopped gating what
the household eats; it only shaped a Menu nobody built.

The immediate trigger was authoring a `protein: dairy` breakfast (the miso
banana chia yogurt pot) and finding the Weekly Layout's rigid `3x sausage, 4x
egg` split had no room for a third protein type — a symptom of a layout designed
for Menu generation that no longer happens.

## Answer

**Full removal.** Menus are retired; a Plan is built, not derived.

### Why not the two lighter options

- **Keep Menus as dead weight.** Two ways to plan a week, one of them unused,
  both needing to stay correct as the pool grows. The orphan check, the layout
  check and the Menu pages would all keep asking for maintenance to describe a
  workflow nobody runs.
- **Just loosen the breakfast split.** Fixes the `dairy` symptom and leaves the
  cause: a layout that gates nothing, read by one skill, generating an artefact
  Plan mode already replaces.

### What went

- `.claude/skills/new-menu/` and `Menus/` (`menu-1.md`, `menu-2.md`).
- In `bin/browse.py`: `layout_violations()`, `orphans()`, `load_menus()`,
  `BREAKFAST_SPLIT`, `LUNCH_TYPES`, `LUNCH_FLOOR`, `FIXED_DINNERS`,
  `FAKEAWAY_DAY`, `FREE_DINNER_DAY`, the `#menus`/`#menu` routes and their two
  views, and the Recipe-detail **Used by** cross-link.
- `GOALS.md`'s whole Weekly Layout section, plus the Macro Bands paragraph
  asserting breakfasts split into exactly two protein clusters — the same
  staleness one section lower.
- 11 tests in `tests/test_browse.py` (`WeeklyLayout`, `Orphans`, and the four
  Menu-dependent cases), replaced by one that checks every Plan fills 28 Slots.
  69 tests become 59.

### What replaced it

`plan-the-week` steps 2 and 3 collapse into one: the grid comes from Plan mode's
checkout, or from a blank 28-Slot grid for a week that declines the page. Steps
renumber 2–6, and Plan mode's own checkout copy now cites step 2.

**The orphan check is not re-pointed at `Plans/`.** Measured against weeks
actually eaten it would flag almost the whole pool today, since one Plan exists
and 51 Recipes do. A warning that fires on everything is noise. If enough Plans
accumulate that "no week has ever used this" becomes a real signal, that is a
new ticket.

**A Plan already stored its own full resolved grid**, so nothing was lost in the
data: the `menu:` frontmatter key was a provenance note, not a dependency. It is
stripped from `Plans/2026-09-14.md` and from `bin/shopping-list.py`'s
`render()`, which now names the Plan itself as the source.

### The narrowing worth naming

`new-recipe` used to take gaps from two callers; it now takes them from
`plan-the-week` alone. Commissioning a Recipe is therefore tied to a real week
having a hole in it, rather than to assembling a rotation in the abstract. That
is a genuine change to how the pool grows, and it is the one thing here that
could want revisiting — if the pool starts growing only reactively and the
household notices the variety narrowing, the answer is a ticket about growing
the pool deliberately, not a Menu.

### Kept

`dairy` as a protein type, the chia pot Recipe, Macro Bands, Nutrient Goals,
Pins, harvesting, basket-filling and shopping-list generation are untouched. The
map's resolved tickets keep their Menu references: they record what was true
when they were written, and this ticket is the reversal.
