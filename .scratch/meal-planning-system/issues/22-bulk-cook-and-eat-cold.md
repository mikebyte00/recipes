# How A Plan Records Bulk-Cook And Eat-Cold

Type: grilling
Status: open
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
