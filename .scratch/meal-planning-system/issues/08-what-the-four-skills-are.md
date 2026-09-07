# What The Four Skills Are

Type: grilling
Status: open
Blocked by: 05

## Question

What are the four skills' boundaries, inputs and outputs?

Sketched so far: generate a Recipe; generate a Menu; run a weekly planning
session that produces a Plan; and turn that Plan into shopping output — a
pasteable Multi-search block for Waitrose, counter lists for Soutars and Dorset
Meats, and a flagged list of Unpinned items.

The fourth skill is **not** basket automation; that is parked. See
[Can Claude Drive Waitrose](01-can-claude-drive-waitrose.md).

Grill the seams, not the features:

- Is "plan the week" one skill or two? Choosing a Menu and editing it into a
  Plan is a conversation; turning a Plan into a shopping list is a
  deterministic transform. Those have very different shapes.
- Does Menu generation call Recipe generation when the pool cannot satisfy
  `GOALS.md`, or does it fail and tell you what is missing?
- What does each skill read and what does it write? Anything writing to the
  pool needs to say so plainly.
- Which of these genuinely need to be skills at all, rather than a script the
  agent runs?

The authoring of each skill is downstream of this and stays in the fog until
the seams are settled.

## Comments

**Unblocked** — [Where Everything Lives](05-where-everything-lives.md) is
resolved. The layout each skill reads and writes:

```
GOALS.md  VOCABULARY.md  PINS.md
Recipes/  Menus/  Plans/  Orders/
```

Three settled facts that constrain the seams this ticket has to grill:

- **Shopping output is a regenerated section inside the Plan**, not a separate
  artifact. So the fourth skill writes back into `Plans/YYYY-MM-DD.md` rather
  than producing a file — which bears directly on "is plan-the-week one skill
  or two".
- **A Plan stores its full resolved grid**, not a diff against its Menu. Menu
  selection therefore *copies*; it does not reference.
- **`Orders/HARVEST.md` already exists and works** — a fifth procedure, agent-
  driven, outside the four. Worth deciding whether harvesting is a skill in its
  own right or a step inside weekly planning, which overlaps the cadence
  question on [Harvesting Past Orders](09-harvesting-past-orders.md).
