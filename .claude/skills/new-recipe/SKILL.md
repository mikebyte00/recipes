---
name: new-recipe
description: "Write or edit a Recipe in Recipes/ — the only writer to the Recipe pool. Holds the corpus bar, resolves every ingredient against PINS.md, and checks the result against VOCABULARY.md and GOALS.md. Use when a Recipe is wanted, when a Plan names a gap the pool cannot cover, or when an existing Recipe changes."
---

# New recipe

The Recipes in `Recipes/` **define the bar**. This skill's whole job is holding
it: the format is a template, but a Recipe that out-cooks its neighbours fails
the project even when it hits the macros.

**Writing to the pool is the user's decision.** `plan-the-week` names a gap and
points here; it never mints a Recipe on its own. Confirm the brief before
writing a file.

Read `VOCABULARY.md` for the closed value lists and `GOALS.md` for the Macro
Bands.

## Steps

1. **Fix the brief.** A Recipe is a `slot`, a `protein` and a band. Say all
   three back to the user before going further — *"a chicken lunch at ~45g /
   ~380 kcal"*. A gap handed over by `plan-the-week` arrives precise; a gap the
   user describes in food terms usually does not.

2. **Read the neighbours.** The Recipes already in that slot with that protein:

   ```bash
   grep -l '^slot: <slot>' Recipes/*.md | xargs grep -l '^protein: <protein>'
   ```

   Read **three of them in full**, method included. Then state their ingredient,
   appliance and step counts back — those three numbers are the bar, and this
   step is done when you can quote them. Reading about the bar in
   [The bar](#the-bar) is not reading the neighbours; a corpus median steers a
   draft far harder than an adjective does.

   Puddings carry no protein, so `grep -l '^slot: pudding' Recipes/*.md` is the
   whole set. It is the smallest slot — read all of it.

3. **Resolve every ingredient against `PINS.md`** before drafting a line. Each
   ingredient is a `lower-kebab-case` key, and the Pin decides the unit:

   ```bash
   .venv/bin/python - <slug> <slug> ... <<'PY'
   import sys; sys.path.insert(0, 'bin')
   pins = __import__('shopping-list').load_pins('.')
   for key in sys.argv[1:]:
       pin = pins.get(key)
       if pin is None:
           print(f"{key:<24} UNPINNED -- quantify it in any sensible unit; add no Pin")
       elif pin.get('staple'):
           print(f"{key:<24} STAPLE   -- omit qty and unit, or use unit: {pin.get('unit')}")
       else:
           print(f"{key:<24} unit: {pin.get('unit')}   ({pin.get('store')})")
   PY
   ```

   The probe reads `PINS.md` for you, so the unit reaches the Recipe without
   passing through your memory. See [The Recipe/Pin rule](#the-recipepin-rule).

4. **Write `Recipes/<slug>.md`.** The slug is the title in `lower-kebab-case`,
   and the **filename is the Recipe's identity** — a Plan cites it.
   Fields in this order, `protein` omitted on a pudding:

   ```markdown
   ---
   title: Title Case Of The Slug
   slot: dinner
   protein: beef
   effort: medium
   tags: []
   appliances: [rice-cooker, ninja-sizzle]
   macros: { protein_g: 46, kcal: 760 }
   ingredients:
     - { ingredient: sirloin-steak, qty: 300, unit: g }
     - { ingredient: parmesan, qty: 50, unit: g, prep: grated }
     - { ingredient: salt, qty: 1, unit: pinch }
   ---

   1. One numbered step per stretch of cooking.
   ```

   `qty` is for **2 people** — the project constant, never a field. `prep` is
   knife-work, `note` is the product or a clarification. `effort` is judged on
   pans and parallelism by `VOCABULARY.md`'s rules and then **stored**, never
   recomputed. `tags` are capability, not intent.

5. **Check it, then report.**

   ```bash
   .venv/bin/python - Recipes/<slug>.md <<'PY'
   import sys, os, re; sys.path.insert(0, 'bin')
   sl = __import__('shopping-list')
   path = sys.argv[1]; slug = os.path.basename(path)[:-3]
   front = sl.load_frontmatter(path)
   V = {'slot': ['breakfast','lunch','dinner','pudding'],
        'protein': ['sausage','egg','tofu','quorn','chicken','white-fish','oily-fish','beef'],
        'effort': ['low','medium','high'],
        'appliances': ['skillet','air-fryer','ninja-sizzle','rice-cooker','pot','toaster','poacher'],
        'tags': ['fakeaway','bulk-cook','eat-cold']}
   bad = [f"{f}: {front.get(f)!r} is not in VOCABULARY.md" for f in ('slot','effort') if front.get(f) not in V[f]]
   bad += [f"{f}: {v!r} is not in VOCABULARY.md" for f in ('appliances','tags') for v in front.get(f) or [] if v not in V[f]]
   p = front.get('protein')
   if front.get('slot') == 'pudding':
       bad += ["a pudding carries no protein"] if p else []
   elif p not in V['protein']:
       bad += [f"protein: {p!r} is not in VOCABULARY.md"]
   if not re.fullmatch(r'[a-z0-9-]+', slug):
       bad += [f"slug is not lower-kebab-case: {slug}"]
   try:
       sl.check_rule({slug: front}, sl.load_pins('.'))
   except sl.Failure as e:
       bad += str(e).splitlines()[1:]
   steps = len([l for l in open(path).read().split('---', 2)[2].splitlines() if re.match(r'^\d+\.', l.strip())])
   m = front['macros']
   print(f"{front.get('slot')}  ~{m['protein_g']:g}g protein  ~{m['kcal']:g} kcal"
         f"  |  {len(front['ingredients'])} ingredients, {len(front.get('appliances') or [])} appliances, {steps} steps")
   print("\n".join(["FAILED:"] + [b.strip() for b in bad]) if bad else "clean: vocabulary and the Recipe/Pin rule both pass")
   sys.exit(1 if bad else 0)
   PY
   ```

   Exit 1 is fatal: an unrecognised value or a broken Recipe/Pin rule makes the
   Recipe unusable by every consumer downstream. Fix it and run again.

   Then put three things in front of the user: the **counts line** beside the
   neighbours' counts, the **macros** against the band, and every **Unpinned**
   ingredient, which they will add to the order by hand the first time.

**Done when** `Recipes/<slug>.md` exists, the check exits 0, and the user has
seen its counts, its macros and its Unpinned ingredients.

## The bar

Measured across the pool, not remembered. **Land inside your slot's row**, and
inside the neighbours' numbers where those are tighter.

| Slot | Ingredients | Appliances | Steps |
| --- | --- | --- | --- |
| Breakfast | 3–8, median 6 | 1–3 | 2–5 |
| Lunch | 4–7, median 6 | 1–2 | 3–5 |
| Dinner | 7–12, median 9 | 1–3 | 3–6 |
| Pudding | 4–5 | 0 | 4 |

These ranges were measured when the pool was smaller. If a slot's neighbours
now sit outside its row, **the corpus is right and the row is stale** — say so
rather than forcing a draft to match the table.

`CLAUDE.md`'s "three to six ingredients" describes breakfast, lunch and pudding.
A **dinner** plates a protein, a grain and a green, and runs 7–12 — the corpus
is the authority on its own bar.

Whole foods, low sugar, protein-forward. A dish assembled in a bowl beats one
built from a sauce made from scratch, and every method in the pool is written to
be cooked on a weeknight.

## The Recipe/Pin rule

An ingredient line takes exactly one of three shapes:

| Shape | When |
| --- | --- |
| `{ ingredient: x, qty: 300, unit: g }` in the **Pin's own unit** | the Pin is not a Staple |
| `{ ingredient: x }`, no `qty`, no `unit` | the Pin is a Staple |
| `{ ingredient: x, qty: 2, unit: whatever fits }` | **Unpinned** — no Pin row exists |

A unit disagreeing with its Pin is an error at list time, never a conversion to
attempt: `bin/shopping-list.py` refuses to sum a Plan that holds one.

## Unpinned

An ingredient with no Pin is an **absence, and the designed path** — the
shopping list flags it, the user buys it by hand, and the next harvest Pins it
from the order history. Writing a Pin row here would guess a product nobody
bought. `PINS.md` is written by harvesting, not by Recipe authoring.

## The macros are approximations

Estimate `protein_g` and `kcal` per person for a serving of 2, store them as
bare numbers so a Plan can sum them, and write `~` on every figure
you show the user. The band is a target, not a gate — bands are checked at the
**day**, in `plan-the-week`, and a Recipe at the edge of its range is fine when
the day still clears ~120g protein under ~1800 kcal.
