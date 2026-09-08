# Author The New-Menu Skill

Type: task
Status: resolved
Blocked by: 08

## Question

Write `.claude/skills/new-menu/SKILL.md`.

Reads `GOALS.md`'s 28-Slot Weekly Layout and `Recipes/`; writes
`Menus/menu-N.md` as structured references, no prose.

The ruling that shapes it: **a Menu that cannot be filled fails and names the
gap precisely** — *"needs a 3rd sausage breakfast under 490 kcal"*, never *"pool
too small"*. It never calls `new-recipe`. See
[What The Four Skills Are](08-what-the-four-skills-are.md).

A Menu is **complete or it is not a Menu**: 28 of 28. Saturday's dinner is the
Menu's own choice; dropping a meal is a Plan-level act, settled in
[Complete The Weekly Layout](14-complete-the-weekly-layout.md).

## Answer

`.claude/skills/new-menu/SKILL.md` is written, **model-invoked**, and every
step of it was run before it was called done.

### Model-invoked, and it does not chain

Same reasoning as `new-recipe`, `plan-the-week` and `shopping-list`: the cost of
not firing is a Menu improvised by hand against a grid the same `load_grid`
treats as fatal when short. Unlike `plan-the-week` it **never chains anywhere**
— a Menu is a standing artifact in `Menus/`, read by `plan-the-week` on demand,
not the start of a pipeline that ends in a shopping list. Nothing downstream
needs it to fire again.

### It never calls `new-recipe`, and step 3 is where that rule lives

`new-menu` fills from the pool and stops at a gap; it does not mint. The
ticket's line — *"needs a 3rd sausage breakfast under 490 kcal", never "pool
too small"* — is written into step 3 as the completion criterion for a stop:
the failing Slot, the constraint, and why the pool cannot meet it. Whether to
grow the pool is the user's call, not this skill's — [Grow The Pudding
Pool](15-grow-the-pudding-pool.md) already exists as evidence that a thin pool
is surfaced as a ticket, not silently absorbed.

### The seams: a fixed table, two floors, one free choice

`GOALS.md`'s Weekly Layout collapses to one table the skill fills against:
six of seven dinners are fixed by day (protein type, not Recipe), breakfast is
a 3/4 split, lunch is a **floor** of 2 tofu / 2 chicken out of 7 — `GOALS.md`
already carries this as a floor, not a ratio, per [Complete The Weekly
Layout](14-complete-the-weekly-layout.md), and the skill states it plainly so a
reader does not over-apply the number as a target — and Saturday's dinner is
free, whatever protein type the week is thinnest on.

### Verbatim by construction, same shape as the other three

A step-2 probe groups the pool by `(slot, protein)` with macros, so a fill is
chosen from real numbers rather than a remembered list. A step-5 check reuses
`bin/shopping-list.py`'s own loaders **unmodified** — `load_grid` accepts a
Menu's `days:` block without change, because it is exactly the shape a Plan's
grid is — so completeness, slug resolution and the Recipe/Pin rule are checked
by the one piece of code authorised to check them. No second `bin/` entry.

### Running it found the check heredoc actually works, not just reads well

A full dry-run Menu 3 was assembled from the real pool, written to the
scratchpad, and checked with the step-5 script extracted from the SKILL.md.
Clean on completeness, resolution and the Recipe/Pin rule; it correctly
reported three days (Thursday, Saturday, Sunday) under the ~130g floor rather
than blocking, which is the "report, never re-fill on your own" instruction
exercised for real rather than assumed. A second run against a deliberately
bad slug raised `Failure: slug resolves to no Recipe file`, exit 1, confirming
the hard-fail path — same discipline ticket 18 used, run rather than read.

**The dry run was deleted, not added to `Menus/`.** Writing a Menu is the
user's decision to make by naming what it is for, which is step 1.

