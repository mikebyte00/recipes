# Author The New-Recipe Skill

Type: task
Status: resolved
Blocked by: 08

## Question

Write `.claude/skills/new-recipe/SKILL.md`.

Seams settled in [What The Four Skills Are](08-what-the-four-skills-are.md):
reads `GOALS.md` Bands, `VOCABULARY.md`, `PINS.md` and a sample of `Recipes/`;
writes `Recipes/<slug>.md`. **It is the only thing in the system that writes to
the pool.**

Use `writing-for-agents`. The hard part is not the format — it is holding the
bar. `CLAUDE.md` names elaborate cheffy recipes as the failure an agent is most
likely to produce, so the skill must make a reader go and read existing meals
before generating one.

Must enforce the Recipe/Pin rule from `PINS.md`: a quantified line uses its
Pin's `unit` exactly, or has no `qty` and its Pin is a Staple. An Unpinned
ingredient is allowed and becomes an absence — never invented as a Pin.

## Answer

`.claude/skills/new-recipe/SKILL.md` is written, **model-invoked**, and every
step of it was run before it was called done.

### Model-invoked, for the same reason as the other three

The failure of not firing is freelancing straight into the pool. "Add a
raspberry pudding" mid-session with no skill fired gets a Recipe written by hand
against a remembered bar, which is exactly the elaborate-cheffy failure
`CLAUDE.md` names — and the pool is the one artifact every other skill reads.
The price is one always-loaded description; against four skills, cheap.

Model-invocation is **not** a licence to chain. [What The Four Skills
Are](08-what-the-four-skills-are.md) ruled that `new-menu` names its gap and
stops, so the skill opens by saying writing to the pool is the user's decision.
Discoverability and autonomy are separate things, and the skill draws the line
itself rather than leaving it to the caller.

### The bar is a measured table, because an adjective does not steer

The hard part was never the format. The lever found was **replacing adjectives
with the corpus's own numbers**, in two places that reinforce each other:

- **Step 2 makes the agent read three neighbours** — same slot, same protein —
  and its completion criterion is *stating their ingredient, appliance and step
  counts back*. Checkable, and it cannot be satisfied by reading the skill.
- **A measured per-slot table**, so a draft has a number to land inside.

| Slot | Ingredients | Appliances | Steps |
| --- | --- | --- | --- |
| Breakfast (13) | 3–8, median 6 | 1–3 | 2–5 |
| Lunch (8) | 4–7, median 6 | 1–2 | 3–5 |
| Dinner (12) | 7–12, median 9 | 1–3 | 3–6 |
| Pudding (4) | 4–5 | 0 | 4 |

**Measuring found a false premise, as every session that measured has.**
`CLAUDE.md` says "few ingredients — often three to six". True of breakfast,
lunch and pudding; **false of dinner**, which runs 7–12 with a median of 9,
because a dinner plates a protein, a grain and a green. Twelve of the 37
Recipes sit outside the stated bar. The skill records the measurement and says
the corpus is the authority on its own bar; `CLAUDE.md` is left for the user,
since it is their instruction file, not the skill's.

### Two heredocs, so units and checks never pass through the agent

Same **verbatim by construction** shape as `plan-the-week` and `shopping-list`,
and no second `bin/` entry — both import `bin/shopping-list.py` and reuse its
loaders.

- **A Pin probe at step 3**, run *before* drafting a line: it prints each
  slug's unit, or `STAPLE`, or `UNPINNED`. The Recipe/Pin rule is then followed
  by construction rather than remembered.
- **A check at step 5**: closed-vocabulary values, the pudding/protein rule, the
  slug shape, and `check_rule` on the single Recipe. It **collects all failures
  and exits 1** rather than raising on the first, because the natural shape —
  `check_rule` raising — hid every vocabulary error behind a traceback. Found by
  running it against a deliberately bad file, not by reading it.

### Running it earned its keep again

Authoring ended by running every step: the `grep | xargs grep` neighbour query,
the probe, and a full dry-run draft — a pudding, written to the scratchpad and
verified with the step-5 script **extracted from the SKILL.md**, so a
transcription error would have shown. It came back clean and inside the pudding
row, and it exercised all three ingredient shapes: a quantified Pin (`lime`),
a Staple carrying its own unit (`honey`), and an Unpinned (`desiccated-coconut`).

**The dry run was deleted, not added to the pool.** Writing a Recipe is the
user's decision, which is the rule the skill itself states. [Grow The Pudding
Pool](15-grow-the-pudding-pool.md) is where puddings get added.

