# Author The Plan-The-Week Skill

Type: task
Status: resolved
Blocked by: 08, 22

## Question

Write `.claude/skills/plan-the-week/SKILL.md`. This is the weekly workflow —
the thing the project exists to make cheap.

**Step 1 is the harvest**, following `Orders/HARVEST.md`, before a Menu is
chosen: the order that just landed is last week's, so its new Pins should serve
this week. A no-op harvest is nearly free. Settled in
[What The Four Skills Are](08-what-the-four-skills-are.md), on top of
[Harvesting Past Orders](09-harvesting-past-orders.md) §3.

Then: choose a Menu, **copy** its grid (a Plan stores its full resolved grid,
never a diff), and edit it — days out, Recipes swapped, meals eaten out. Writes
`Plans/YYYY-MM-DD.md`, named for the week's Monday.

It **sums each day** and reports a miss against the ~130g floor or the ~1800
kcal ceiling. **Reports, never blocks** — 5 of 14 corpus days already miss the
floor.

Blocked on [How A Plan Records Bulk-Cook And Eat-Cold](22-bulk-cook-and-eat-cold.md),
which decides what a Plan's grid can carry.

## Answer

**Written, and every step run before it was called done** —
`.claude/skills/plan-the-week/SKILL.md`, six steps and three reference sections.
**Model-invoked**, and it **chains** into `shopping-list` rather than handing the
user an invocation.

### Model-invoked, because the failure of not firing is freelancing

The cost of a missed user-invoked skill is normally that the user retypes. Here
it is worse: "let's plan next week" mid-session, with no skill fired, gets a Plan
improvised by hand — the exact freelancing this skill exists to prevent, against
a 28-Slot grid the script treats as fatal when it is short. `writing-for-agents`
sets the bar at "the agent must reach the skill on its own", and this clears it.
Same reasoning as [Author The Shopping-List
Skill](21-author-shopping-list.md), and consistent with it.

### It chains, which is what ticket 21 left open

[What The Four Skills Are](08-what-the-four-skills-are.md) seamed the two skills
on **re-runnability** — you regenerate the list whenever the Plan changes. That
argument is about the *second* run and every one after; it says nothing against
the first. A Plan with no shopping section is a half-done job in a project whose
whole purpose is the time cost of assembling the order, so step 6 invokes
`shopping-list` against the Plan just written. The seam survives intact: the
Wednesday swap still re-runs `shopping-list` alone, which is the case it was cut
for.

### The harvest is offered, not assumed

Step 1 stays the harvest, as [What The Four Skills
Are](08-what-the-four-skills-are.md) placed it, but the skill **asks** before
opening a browser session against the user's signed-in Waitrose account. A
no-op harvest is nearly free only once the browser is open; getting there is
not. Skipping it is safe and the skill says why: this week's new ingredients
come out **Unpinned**, which is the designed path already, and the next harvest
Pins them.

### Three things authoring forced

- **A Plan's grid is lifted by `awk`, not transcribed.** The same
  verbatim-by-construction move ticket 21 made for the shopping section: all 28
  Slots arrive without passing through the agent. `menu:` and `title:` are
  written above it, and the copy was verified at 28 Slots.
- **`menu:` is now exercised.** [Where Everything
  Lives](05-where-everything-lives.md) mandated the field and
  `bin/shopping-list.py` has always read it as provenance, but no file ever
  carried one — Menus fall back to their source path. A Plan's shopping
  section now opens `Generated from Menus/menu-2.md`.
- **A day holding an `eaten-out` Slot is reported but not judged.** Found by
  running step 5, not by reading it: two Saturday Slots out dropped the day to
  ~73g and it duly reported UNDER the floor — a false alarm, since the household
  ate, just not from the grid. False alarms train the user to ignore the report,
  so the check is suppressed and the reason printed.

### Verified on a throwaway Plan

Menu 2 copied, two Saturday Slots set `eaten-out`, Monday's lunch swapped, and
Tuesday's lunch pointed at the same slug to spell a doubled batch:

- the grid copies at **28 Slots** and the `menu:` field renders as provenance
- day sums are correct, with Saturday **not judged** and Tuesday lifted off its
  ~129g miss by the swap
- the chain produces **39 lines** (33 Waitrose, 4 Soutars, 2 Dorset Meats),
  7 Unpinned, **0 flags**, down from Menu 2's 42
- the splice is **idempotent** across two runs, and the week note written above
  `## Shopping` survives regeneration

The step-5 command was extracted back out of the SKILL.md and run from there, so
what was tested is what the file says.

### It corrected a number the map was carrying

Summing the days reproduced [Raise The Weak Days](16-raise-the-weak-days.md)'s
table exactly — and that table has **six** rows where its prose said five. The
map, the ticket and two handoffs all carried `five`. Corrected in ticket 16;
the skill says six.

### The day sum is a command, not a second `bin/` entry

`CLAUDE.md` authorises exactly one piece of code, and this skill needed to add
28 macro figures into 7 day totals. Doing that in prose is the silent-error case
[What The Four Skills Are](08-what-the-four-skills-are.md) wrote the script to
avoid, so the arithmetic is a heredoc **inside the SKILL.md** that imports
`bin/shopping-list.py` and reuses its loaders. No file is added to `bin/`,
nothing new is importable, and the command is re-read from disk every run. If a
second consumer ever wants these day sums, that is the moment to raise the
`bin/` entry as a ticket.
