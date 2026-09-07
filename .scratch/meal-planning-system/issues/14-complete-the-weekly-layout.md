# Complete The Weekly Layout

Type: grilling
Status: resolved
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

## Answer

**A Menu is 28 Slots and both are now complete.** Resolved 07 September 2026.
`GOALS.md`'s Weekly Layout rewritten, `CONTEXT.md`'s Fakeaway entry sharpened,
8 `null`s filled.

### Three of this ticket's premises were wrong

- **The Fakeaway question was already answered.** `VOCABULARY.md` says
  `fakeaway` is "independent of `protein`: chicken in menu 1, lemon sole in
  menu 2". This ticket asked whether it occupies a protein type; the vocabulary
  had already said no. What was actually wrong was `GOALS.md`, which listed
  "1x Fakeaway" alongside "1x Chicken Dinner" and so **double-counted a dinner
  that already had a protein type**.
- **The unassigned dinner is Saturday, not Friday.** This ticket guessed "the
  Fakeaway is presumably Friday or Saturday". Both Menus put it on **Friday** —
  Menu 2's `the-combo-lemon-sole-plate-air-fryer-chips` is fish and chips,
  tagged `fakeaway`, and is also that Menu's third white-fish dinner. Re-counted
  with Fakeaway as a tag, six of the seven dinners were already fixed by day.
- **Pudding repeats were never a decision.** The ticket asks whether repeats are
  "fine". Both Menus already used all four pudding Recipes across five Slots, so
  once pudding went nightly the best any Menu can do is three Recipes twice and
  one once. There was nothing to decide, only something to record: see
  [Grow The Pudding Pool](15-grow-the-pudding-pool.md).

### Decisions

1. **Pudding is nightly; a Menu is 28 Slots.** Not a taste call — a measured
   one. Summing every complete day in the corpus **with the pudding removed**,
   the best day reaches 124g and the average 118g, against a ~130g floor:
   **0 of 10 days clear it without pudding, where 5 of 10 clear it with.**
   Pudding is the most protein-efficient Slot in the corpus, 11–13.5g for
   120–170 kcal. `CONTEXT.md`'s "never partial" stands unamended, and this
   **retires the map's "what a no-pudding day targets" fog** — there is no
   no-pudding case.

2. **Saturday is filled, and the Plan removes it.** Both Menus dropped exactly
   Saturday's lunch, dinner and pudding plus Friday's pudding — identically,
   across two independently-written weeks, which reads as structure. It was put
   to the user as a real question rather than assumed: is Saturday reliably
   eaten out? The answer is that it varies, so **the Menu offers seven days and
   the Plan takes out what it needs**, consistent with
   [Per-Slot Macro Bands](06-per-slot-macro-bands.md) ruling that dropping a
   meal is a Plan-level act. A Saturday dinner you skip costs nothing; not
   having one when you are in costs a week's planning.

3. **Lunch is a floor, not a ratio: 7 lunches, tofu or chicken, at least 2 of
   each.** `GOALS.md` asked for 3 tofu / 2 chicken. Menu 1 runs 4 chicken /
   2 tofu and Menu 2 runs 5 tofu / 1 chicken — not merely off the ratio but
   leaning **opposite ways**, and no single-Slot fill can bring either near it.
   Same reasoning as 06's kcal ceiling: two independent weeks ignoring a number
   means the number is wrong. The new rule is one both Menus satisfy.

4. **Saturday is the free dinner.** Every type it could be fixed to is spoken
   for: a third white fish makes 3 of 7, a second oily fish means salmon twice,
   a second steak means red meat twice, and chicken would give Menu 1 three
   chicken dinners counting the Fakeaway. Six dinners fixed by day, the seventh
   chosen per Menu — which is what the two Menus were already doing.

5. **Fakeaway is a day convention, not a Slot in the protein budget.** Friday,
   in both Menus. `GOALS.md` corrected; `CONTEXT.md`'s Fakeaway entry now says
   so and drops the vaguer "intended for weekend slots".

### The fills

| Menu | Slot | Recipe |
| --- | --- | --- |
| 1 | Friday pudding | `zesty-lemon-vanilla-bean-cheesecake` |
| 1 | Saturday lunch | `creamy-mild-curry-tofu-butter-beans` (tofu) |
| 1 | Saturday dinner | `creamy-florentine-salmon-...` (oily fish) |
| 1 | Saturday pudding | `the-real-salted-peanut-butter-mousse` |
| 2 | Friday pudding | `the-real-salted-peanut-butter-mousse` |
| 2 | Saturday lunch | `creamy-pesto-chicken-cannellini-beans` (chicken) |
| 2 | Saturday dinner | `korean-gochujang-glazed-chicken-...` (chicken) |
| 2 | Saturday pudding | `zesty-lemon-vanilla-bean-cheesecake` |

Chosen for protein density under the kcal ceiling, per the ruling that the
filled days should be built from the dense end of each pool. Every new day
clears ~130g except Menu 1's Saturday at ~129.5g — half a gram short, and still
a better day than five of the seven in that Menu. **No day breaches the ~1800
kcal ceiling**; the highest is ~1760, unchanged from before. Both Menus reach
the minimum possible pudding repetition.

Menu 2's Saturday runs chicken at both lunch and dinner. Accepted: the two
dishes share nothing but a protein, and the alternative was a second salmon
night or a fourth white fish.

### Surfaced, and ticketed rather than absorbed

- [Grow The Pudding Pool](15-grow-the-pudding-pool.md) — 4 Recipes for 7 nightly
  Slots forces repeats arithmetically, and the four are variations on one idea.
- [Raise The Weak Days](16-raise-the-weak-days.md) — 5 of 14 days miss the
  protein floor by 0.5–7.5g. Four of the five were short before this ticket
  touched anything, so filling `null`s could never have fixed them. **Both
  Sundays and both Thursdays are short**, which looks structural rather than
  incidental.
