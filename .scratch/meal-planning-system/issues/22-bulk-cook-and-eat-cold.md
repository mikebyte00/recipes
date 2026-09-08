# How A Plan Records Bulk-Cook And Eat-Cold

Type: grilling
Status: resolved
Blocked by: —

## Question

`bulk-cook` and `eat-cold` are Recipe **capabilities** — settled in
[The Tag Vocabulary](03-the-tag-vocabulary.md), which ruled that a tag says what
a Recipe *can* do and never what a given week did with it.

So a week that actually acts on one has nowhere to say so, and two things break:

- **A doubled batch has to reach the shopping list doubled.** Cooking four
  portions on Monday means buying for four.
- **A meal eaten cold on Tuesday was cooked on Monday.** Tuesday's Slot is
  filled, but nothing is cooked in it.

Does a Plan's grid slot carry a multiplier, a back-reference to the Slot that
cooked it, both, or neither? Neither is a live answer: the household may simply
not use these tags in practice, and inventing a representation for an unused
capability is the kind of speculative field this project has rejected before.

Graduated from the map's fog by
[What The Four Skills Are](08-what-the-four-skills-are.md), which made it sharp:
the grid now has a consumer that parses it. This **blocks**
[The Shopping List Script](17-the-shopping-list-script.md) and
[Author The Plan-The-Week Skill](20-author-plan-the-week.md), because both need
to know what a Plan slot can hold.

## Answer

**Neither.** A Plan Slot gains no multiplier, no back-reference, and no note
field. The ticket's premise was false in two places, and the corpus was already
doing the thing it worried about.

### A doubled batch does not change the shopping list

A Recipe serves 2. Two Slots need 4 portions. Buying twice the ingredients gets
4 portions whether it is one pan of 4 or two pans of 2 — and the script sums
quantities *before* the `ceil()` to packs, so even the rounding lands
identically. The ticket claimed "cooking four portions on Monday means buying
for four." It already does: a Menu is 28 filled Slots, so there is nowhere for a
portion to go that the grid is not already paying for.

Confirmed with the user: **no portion is ever cooked that the grid does not
hold.** No freezer stash, no off-grid packed lunch. That was the only case that
could have resurrected a multiplier.

### Doubling is spelled "the same Recipe in both Slots"

The mechanism already exists. `CONTEXT.md` defines a Plan as a Menu with days
removed and Recipes swapped; deciding at Plan time to bulk-cook Tuesday's lunch
and drop Wednesday's is a **swap** — Wednesday's Slot becomes Tuesday's Recipe.
The sums are identical to a doubled batch, and the dropped Recipe's ingredients
fall out of the list on their own. No new field expresses anything the swap
cannot.

### The corpus was already bulk-cooking, silently

Both Menus repeat a **lunch on adjacent days**:

| Menu | Days | Recipe |
| --- | --- | --- |
| 1 | Tue/Wed lunch | `creamy-pesto-chicken-cannellini-beans` |
| 2 | Tue/Wed lunch | `creamy-mild-curry-tofu-butter-beans` |
| 2 | Thu/Fri lunch | `lemon-herb-lentil-tofu-pan` |

Every one is a lunch, never a dinner — and lunch is the meal with no reheat,
which is exactly the `eat-cold` definition. The user confirmed this is one cook
for two days. The pudding repeats (Mon/Sat, Tue/Fri, Thu/Sun in Menu 1) are
**non-adjacent** and are pool scarcity, which belongs to
[Grow The Pudding Pool](15-grow-the-pudding-pool.md), not here.

So the pattern this ticket set out to represent has been in the corpus from the
start, expressed with zero machinery, and it shopped correctly the whole time.

### The tags stay, and gain a standing rule

**0 of 37 Recipes carry `bulk-cook` or `eat-cold`.** Against
[The Tag Vocabulary](03-the-tag-vocabulary.md)'s own rule 2 — extend on first
real use, do not pre-stock values nothing cooks, which is why `beans` is
deliberately absent — both were pre-stocked. They are **kept anyway**: they are
honest properties of a dish, and re-adding a deleted value costs the same line
as leaving it.

The price of keeping them is a rule, now written into `VOCABULARY.md` beside the
definitions: **`bulk-cook` and `eat-cold` have no consumer.** Recipe generation,
Menu building, weekly planning and the shopping list all ignore them. This
closes the loophole where a later skill invents a meaning for a value nothing
had defined a use for. It amends nothing in
[The Tag Vocabulary](03-the-tag-vocabulary.md); it makes rule 3 —
capability, never intent — enforceable.

The 37 Recipes are left untagged. Tagging them would be guesswork about which
dishes survive a night in the fridge, and nothing would read the answer.

### No note field

Considered and **rejected by the user**: an optional free-text `note:` on a Plan
Slot, so a Plan could say *cook Tuesday, eat cold Wednesday* to a reader who was
not in the room. The user cooks, and a Recipe appearing twice on adjacent days
is already unambiguous to them. A Plan Slot holds a Recipe slug and nothing
else.

### What this unblocks

- [The Shopping List Script](17-the-shopping-list-script.md): a Plan Slot is a
  slug. The script needs no multiplier arithmetic and no cross-Slot
  reference — it sums the grid it is given.
- [Author The Plan-The-Week Skill](20-author-plan-the-week.md): the skill offers
  a Recipe swap, which already covers the bulk-cook case. It must **not** offer
  a doubling control.
