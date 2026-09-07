# Complete The Weekly Layout

Type: grilling
Status: open
Blocked by: —

## Question

What protein type fills every one of a Menu's 28 slots, and is pudding nightly?

A [Menu](../../../CONTEXT.md) is complete — 7 days, 4 slots, always. `GOALS.md`
does not specify a complete week:

| Slot | GOALS.md specifies | A complete Menu needs |
| --- | --- | --- |
| Breakfast | 3x sausage, 4x egg = **7** | 7 ✅ |
| Lunch | 3x tofu, 2x chicken = **5** | 7 |
| Dinner | 2x white fish, 1x oily fish, 1x chicken, 1x steak, 1x fakeaway = **6** | 7 |
| Pudding | **nothing** | 7 |

Both existing Menus fill 7 breakfasts, 6 lunches, 6 dinners and 5 puddings,
leaving **4 `null` slots each** — Friday pudding, and Saturday lunch, dinner and
pudding. Identical in both, which read as deliberate structure until
[Per-Slot Macro Bands](06-per-slot-macro-bands.md) established that dropping
meals is a **Plan**-level act. The Menu offers all seven days so there is
something to switch around; the week you actually eat is where meals come out.

### What has to be decided

- **Two more lunches.** The corpus does not follow the 3 tofu / 2 chicken split
  it was given — Menu 1 runs 4 chicken / 2 tofu, Menu 2 runs 5 tofu / 1 chicken.
  So the ratio is up for grabs, not just the count.
- **A seventh dinner.** The existing six are fixed to days in places: Sunday and
  Monday white fish, Wednesday oily fish. The Fakeaway is presumably Friday or
  Saturday. Which day is unassigned, and what fills it?
- **Whether pudding is nightly.** Seven puddings a week may not be wanted. If it
  is not, then a Menu is *not* 28 slots and
  [Per-Slot Macro Bands](06-per-slot-macro-bands.md)'s day arithmetic needs a
  no-pudding case: a 3-slot day targets ~120g, under the ~130g floor.
- **Does the Fakeaway occupy a protein type?** It is a Recipe tag, not a
  protein type, but the layout lists it alongside them.

### Then

Fill the 8 `null` slots across `Menus/menu-1.md` and `Menus/menu-2.md` from the
existing 37 Recipes, and re-check each day against the Bands. Both Saturdays
currently sum to ~22g and ~430 kcal on breakfast alone.

### Watch for

The pool may not cover it. There are only **4 puddings** for what could become
14 pudding slots across two Menus, and repeats are already normal — Menu 1 uses
`the-raspberries-white-chocolate-ganache` twice and
`creamy-pesto-chicken-cannellini-beans` twice. Decide whether that is fine or
whether this ticket surfaces a need for new Recipes.
