# Raise The Weak Days

Type: grilling
Status: open
Blocked by: 14

## Question

Six of the 14 days across the two Menus miss the ~130g protein floor. Do they
get re-pointed at denser Recipes, or is the floor wrong?

Measured after [Complete The Weekly Layout](14-complete-the-weekly-layout.md)
filled the empty Slots:

| Menu | Day | Protein | Short by |
| --- | --- | --- | --- |
| 1 | Thursday | ~124g | 6.0g |
| 1 | Saturday | ~129.5g | 0.5g |
| 1 | Sunday | ~122.5g | 7.5g |
| 2 | Tuesday | ~129g | 1.0g |
| 2 | Thursday | ~126g | 4.0g |
| 2 | Sunday | ~123g | 7.0g |

All but Saturday are **inherited** — they were already short before any Slot was
filled, so filling `null`s could never have fixed them. Ticket 14 explicitly
declined to re-point them, because re-pointing a day that was never empty is a
different act from completing one that was.

### The tension

There is room to fix this: the kcal ceiling is nowhere near threatened. The
highest day is ~1760 against ~1800, and both Menus average ~1660 — roughly
140 kcal/day spare.

But the same reasoning that settled the kcal ceiling and the lunch ratio applies
here too. [Per-Slot Macro Bands](06-per-slot-macro-bands.md) found a corpus
failing its own goals everywhere and concluded the goals were wrong; ticket 14
found a 3-tofu / 2-chicken lunch split that no Menu had ever followed and
replaced it with a floor the corpus meets. **Eight of 14 days clear ~130g and
six miss by 0.5–7.5g** — is that a corpus to correct, or a floor set 5g high?

Note the pattern: **both Sundays and both Thursdays are short.** Sunday runs a
low-protein breakfast (`eggy-bread` 17.5g, `eggs-and-soldiers` 17g) and Thursday
pairs a 46g steak dinner with the day's lightest lunch. That looks structural,
not incidental — which argues the fix is a Recipe or two, not a re-pointing.

**The count above was `five` until it was re-measured.** The table has always
held six rows; only the prose said five, and the error propagated into the map
and two handoffs. Re-summing the days in
[Author The Plan-The-Week Skill](20-author-plan-the-week.md) reproduced all six
values exactly and corrected the count.

### Watch for

Re-pointing changes days that are otherwise fine. Every swap has to be re-summed
against all four Bands, not just protein.
