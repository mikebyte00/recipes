# What The Four Skills Are

Type: grilling
Status: resolved
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

## Answer

**Four skills and one script.** The seams fall on **re-runnability** and on
**mechanical versus judgement**, not on subject matter.

### There is code in this repo, and there is exactly one piece of it

`bin/shopping-list.py`. The transform was measured before it was ruled on:
Menu 1 resolves to 180 ingredient uses → 63 quantified Pins → 24 dropped as
Staples → **39 shoppable lines** (34 Waitrose, 3 Soutars, 2 Dorset Meats).
Aggregation is plain addition — [Normalise Ingredient
Units](12-normalise-ingredient-units.md) made it so — and pack division is one
`ceil()` per Pin. An agent doing that in prose across 180 lines will make silent
arithmetic errors, and a wrong sum produces a wrong shop that nothing catches.

It is also the natural home of the Recipe/Pin rule check that [Normalise
Ingredient Units](12-normalise-ingredient-units.md) deliberately left unwritten:
the consumer that has to apply the rule anyway is the one that should enforce it.

`python3` with `pyyaml` is already present and is how the last three sessions
audited this corpus. **Everything else stays prose, because everything else is
judgement.** This is the ruling `CLAUDE.md` was holding open — no other `bin/`
entry is authorised by it.

### Plan-the-week is two skills, so the sketch stays at four

The pull toward one is real: the shopping output writes *back into*
`Plans/YYYY-MM-DD.md`, the same file, in the same sitting. It loses to a
stronger fact — **you regenerate the shopping section whenever the Plan
changes.** A Wednesday swap needs the list redone; folding the two together
would mean re-running the planning conversation to get it.

| Skill | Reads | Writes |
| --- | --- | --- |
| `new-recipe` | `GOALS.md` Bands · `VOCABULARY.md` · `PINS.md` · a sample of `Recipes/` | `Recipes/<slug>.md` |
| `new-menu` | `GOALS.md` layout · `Recipes/` | `Menus/menu-N.md` |
| `plan-the-week` | `Orders/HARVEST.md` → `Menus/` · `Recipes/` · `GOALS.md` | `Plans/YYYY-MM-DD.md` |
| `shopping-list` | a Plan · runs the script | the Plan's shopping section |

**`new-recipe` is the only thing that writes to the pool.** Anything else that
wants a Recipe asks for one.

### They live in `.claude/skills/`, and `Orders/HARVEST.md` does not move

[Where Everything Lives](05-where-everything-lives.md) ratified `HARVEST.md`
beside its output on a co-location argument. **That argument does not
transfer.** `HARVEST.md` is *read on demand* by a session already doing
something else; these four are *invoked by name*, and invocation needs the
skills directory. `HARVEST.md` stays exactly where it is.

### A Menu that cannot be filled fails and names the gap

`new-menu` never calls `new-recipe`. Writing to the Recipe pool is a large side
effect with its own bar — `CLAUDE.md`'s "the bar for a Recipe" — and chaining
means a Menu request silently mints Recipes nobody reviewed.

The failure must be **precise**: *"needs a 3rd sausage breakfast under 490
kcal"*, never *"pool too small"*. This is already the established pattern —
[Grow The Pudding Pool](15-grow-the-pudding-pool.md) exists because a session
surfaced a thin pool as a ticket instead of quietly filling it.

### The harvest is step 1 of `plan-the-week`

[Harvesting Past Orders](09-harvesting-past-orders.md) §3 already settled that a
harvest runs inside weekly planning; only its position was open. It goes
**first**, because the order that just landed is *last* week's — harvesting it
before choosing a Menu is what makes this week's list benefit from the new Pins,
which is the entire point of the loop. A no-op harvest is nearly free: read
`Orders/history.md`, see nothing new, stop.

### The shopping section carries search terms and line numbers both

All 44 shoppable Waitrose Pins carry **both** a `line_number` and a
`search_term` — 100% coverage, checked, not assumed.

- A pasteable `search_term` block, because that is what Multi-search eats.
- `line_number` beside each item in the table above it, as the escape hatch when
  search misfires. `/ecom/products/x/<n>` resolves on its own.
- Soutars and Dorset Meats render as plain quantities. No line numbers exist for
  them and none ever will.
- **Unpinned items get their own headed list** — those are the ones you add by
  hand, and Menu 1 alone has 14 of them.

That section **is the review step** the map had in its fog: you read the table
and the Unpinned list before anything is pasted. It needed no automation to
exist, because it was never a basket-automation concern.

### Two failure modes, deliberately different

**Hard-fail on a Recipe/Pin rule violation** — a `unit` disagreeing with its
Pin, or a slug resolving to no file. The sum is meaningless; stop.

**Fall back and flag on a missing `pack`** — emit `buy 1` with `⚠ pack unknown`.
Nobody recorded the pack size; that is a data gap, and the week still shops
while the gap stays visible. Three Waitrose Pins are in this state today:
`celery`, `sourdough`, `spring-onions`.

### The script checks the mechanical; the skill reports the judgement

The script enforces the Recipe/Pin rule and Menu completeness — 28 Slots, every
slug resolving to a file.

`plan-the-week` sums each day and **tells** you when it misses the ~130g floor
or breaches the ~1800 kcal ceiling. It reports; it never blocks. `GOALS.md` says
both are rough objectives, [Per-Slot Macro Bands](06-per-slot-macro-bands.md)
put the check on the day rather than the Recipe, and **5 of 14 corpus days
already miss that floor** — a gate would reject the corpus that defines the bar.

### Findings recorded, not fixed here

- **`oat-milk` is `unit: g` against a `pack: 1 litre`.** A one-line Pin fix, not
  a unit-conversion feature for the script to carry.
- **`celery`, `sourdough`, `spring-onions`** have no `pack`.
- **14 ingredients are Unpinned across Menu 1 alone** — `garlic`, `red-onion`,
  `halloumi`, `strawberries` and ten others. Expected: [Confirm And Write The
  Pins](13-confirm-and-write-the-pins.md) left 17 absences on purpose.

### What this retires

[The Query String Generator](10-the-query-string-generator.md) asked whether
`search_term` is a stored Pin field or derived by rules. **It is already a
stored field at 100% coverage** — answered in passing by [Mint The Pin
Catalogue](11-mint-the-pin-catalogue.md) and [Confirm And Write The
Pins](13-confirm-and-write-the-pins.md), and its other half, the output shape,
is settled above. The ticket as written has nothing left, so it was **rewritten
rather than closed**: what was never tested is whether those 44 terms actually
resolve in Multi-search.

### Authoring stays out

The five authoring jobs graduate from the fog as tickets 17–21, written with
`writing-for-agents` per the map's Notes. **No skill was authored in this
session** — this ticket settles seams, and a skill written against an unsettled
seam is a skill rewritten.
