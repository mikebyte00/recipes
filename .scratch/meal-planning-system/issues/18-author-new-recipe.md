# Author The New-Recipe Skill

Type: task
Status: open
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
