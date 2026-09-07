# What A Recipe File Looks Like

Type: prototype
Status: resolved
Blocked by: —

## Question

What is the shape of a single Recipe file?

Build the prototype by converting three real meals from the existing rotations,
deliberately chosen to stress different cases:

- **Zero-Prep Sausage & Chickpea Crisp Hash** — trivial, one appliance, three
  ingredients.
- **Sizzled Sirloin Steak with Rice-Cooker Mushroom & Truffle Grain Pilaf** —
  multiple appliances, a component structure, an ingredient measured in grams
  so small (5g truffle oil) that it is obviously a store-cupboard item.
- **The Raspberries & White Chocolate Ganache** — a pudding that recurs across
  both weeks with *different* macros recorded (170 kcal on Week 1 Thursday,
  242 kcal on Week 1 Sunday). Resolve what that discrepancy means.

Open sub-questions the prototype should settle: frontmatter versus prose;
whether ingredients are structured data or a markdown list; whether "The Pan"
survives as a field; how per-serving macros are recorded; and how a Recipe is
identified so a Menu can reference it unambiguously when two have similar names.

Show the alternatives side by side rather than picking one silently.

## Answer

**Structured frontmatter, prose method.** Candidate A, prototyped at
[prototypes/recipe-format/](../prototypes/recipe-format/).

The seam: structured where machines consume it (ingredients, macros, tags,
appliances), prose where a human consumes it (the method). Candidate B kept
ingredients as prose, which would force the shopping list to re-parse
`1 can chickpeas, drained and patted dry` on every run — importing Waitrose's
ambiguity problem into our own repo. Candidate C structured the method into
`temp_c`/`minutes`, which nothing reasons about and which is miserable to edit.

### The format

```yaml
---
title: Zero-Prep Sausage & Chickpea Crisp Hash
slot: breakfast
protein: sausage          # field, not tag — GOALS.md counts against it.
                          # Confirm in The Tag Vocabulary.
tags: [quick, bulk-cook]
appliances: [air-fryer]
macros: { protein_g: 32, kcal: 385 }
ingredients:
  - { ingredient: vegetarian-sausage, qty: 4,   unit: each, prep: sliced into chunks }
  - { ingredient: chickpeas,          qty: 1,   unit: can,  prep: drained, patted dry }
  - { ingredient: cottage-cheese,     qty: 160, unit: g,    note: to serve }
---

1. Numbered markdown steps. Prose. Read while cooking.
```

`ingredient:` is the canonical key that resolves to a Pin. Everything else about
buying the thing lives on the Pin, never here.

### Settled sub-questions

- **Identity is the filename.** No `id` field — two sources of truth for
  identity is how identity drifts. Menus reference the slug
  (`zero-prep-sausage-chickpea-crisp-hash`). Renaming is a real rename.
- **Recipes list every ingredient, staples included.** The corpus has been
  silently omitting salt, pepper, oil and even the truffle oil named in the
  steak's own title — meaning several recipes cannot be cooked as written.
  Filtering happens at shopping time via the Pin's `staple` flag, so the
  judgement lives in one place rather than baked into 28 files.
  Confirmed staples: **salt, pepper, and all oils including truffle** — they
  survive many weeks without replenishment.
- **No serving count.** Serves 2 is a project constant.
- **`The Pan` survives as `appliances`,** structured. It becomes queryable —
  "no three-appliance dinners on a weeknight" is a real constraint later.
- **No `sizes` concept.** See below.

### The ganache discrepancy — resolved

Not two portion sizes: **an error**. The two versions share a method but differ
in quantities (200g yogurt + 24g chocolate versus 300g + 40g). They were meant
to be identical. The **standard size wins** — 200g/24g, ~170 kcal, ~11g protein.
The larger version is deleted.

Consequence for [Per-Slot Macro Bands](06-per-slot-macro-bands.md): Sunday in
**both** weeks loses ~4.4g protein and ~72 kcal. Week 1 Sunday drops from 126.9g
and Week 2 Sunday from 127.4g — days that already missed the 130–140g target now
miss it by more. Do not silently correct this; it is evidence.

A `sizes` key was prototyped and rejected: every consumer would pay for it
forever to serve one dessert.
