# Snack Slot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A fifth, optional `snack` Slot: a batch baked on one day, bought once, and spread over the 7 days from its bake day in the day totals.

**Architecture:** `bin/shopping-list.py` owns the rules — the grid's optional `snack:` key, the `makes:` check, and `day_macros`, the one place the spread is computed. `bin/browse.py` imports it instead of summing days itself, and its page grows a Snack group, a snack line per day, and a skippable snack step in Plan mode. Prose (VOCABULARY, CONTEXT, CLAUDE.md, two skills, ticket 26) records the decision.

**Tech Stack:** Python 3 stdlib + PyYAML (`.venv/bin/python`), vanilla JS inside `bin/browse.py`'s `TEMPLATE`, `unittest`, `node` for the lifted-JS tests.

**Spec:** `docs/superpowers/specs/2026-10-11-snack-slot-design.md`

## Global Constraints

- No third `bin/` entry. A new **test** file is fine; new code lives in `bin/shopping-list.py` or `bin/browse.py`.
- Run everything with `.venv/bin/python` (build it once: `python3 -m venv .venv && .venv/bin/pip install pyyaml`).
- Any commit that changes `bin/browse.py` (or a Recipe/Plan) regenerates and commits `index.html` in the **same commit**: `.venv/bin/python bin/browse.py`, then `.venv/bin/python bin/browse.py --check` prints `index.html is up to date`.
- The four meal Slots stay required: 28 Slots per grid. `snack` is optional, at most one per day, and never `eaten-out`.
- `makes:` is a positive integer, **required on `slot: snack`, forbidden on every other slot**.
- A snack's ingredient `qty` is for the **whole batch**; its `macros` are **per serving**.
- Spread: a batch baked on day D adds `makes / 2 × per-serving macro / 7` per person to each of D…D+6, clipped at the Plan's Sunday. Overlapping batches add.
- Day totals are rounded to 1 decimal (as today). Every macro figure the page shows keeps its `~` (the `g()`/`kc()` helpers already add it).
- The existing three Plans must keep loading and rendering unchanged.
- Commit messages end with the session's attribution lines; no model identifier in any committed text.

## Review Focus

1. **A Plan whose snack slug names a non-snack Recipe (or a meal Slot naming a snack Recipe)** — the spec is silent; expected: `day_macros` treats it by the *Slot*, not the Recipe's own `slot:` field, and the grid loads. Pinned in Task 1 (`test_a_snack_slot_is_spread_by_its_slot_not_the_recipes`).
2. **`snack:` present but empty (`snack:` with no value, or `snack: null`)** — expected: read as no snack, not as a missing Slot or a crash. Pinned in Task 1.
3. **Browse loads a snack Recipe that lacks `makes:`** (the shopping list never ran) — expected: `bin/browse.py` refuses to write the page with the same message, rather than a `KeyError` traceback. Pinned in Task 2.
4. **Skip on the snack step in Plan mode, then Back onto it** — expected: the snack key is *absent* (never `eaten-out`), the meal count stays at 28, and Checkout stays enabled. Pinned in Task 4 (`planYaml` omits it; progress counts meals only).
5. **A past Plan with no snack keys** — expected: payload day totals equal the old meal-only sums exactly. Pinned in Task 2 (`test_a_week_with_no_snack_sums_as_before`).

## File Structure

| File | Change |
|---|---|
| `bin/shopping-list.py` | `SNACK`, optional snack in `load_grid`, `check_makes`, `day_macros` |
| `tests/test_shopping_list.py` | **new** — fixtures + the rules above |
| `bin/browse.py` | import shopping-list; payload totals from `day_macros`; drop `day_totals`; `makes` in rows; page changes; Plan mode snack step |
| `tests/test_browse.py` | replace `DayTotals`, add payload, `weekRows` and `planYaml` cases |
| `index.html` | regenerated with every `bin/browse.py` commit |
| `VOCABULARY.md`, `CONTEXT.md`, `CLAUDE.md`, `.claude/skills/plan-the-week/SKILL.md`, `.claude/skills/new-recipe/SKILL.md`, `.scratch/meal-planning-system/issues/26-the-snack-slot.md`, `.scratch/meal-planning-system/map.md` | prose |

**Deliberate departure from the spec:** §3 says `browse.py`'s `day_totals` "stops counting the snack key". Once the payload reads `day_macros`, `day_totals` has no caller, so it is **deleted** and its test moves to `day_macros`. Also, §3's "a day holding an `eaten-out` meal is still not judged" is read as *today's* behaviour, which only skips judging a day with **no** meal cooked at home (`flags` only when `cooked > 0`) — that is unchanged.

---

### Task 1: The rules in `bin/shopping-list.py`

**Files:**
- Modify: `bin/shopping-list.py` (constants at top, `load_grid`, new `check_makes` and `day_macros` after `check_rule`, `main`)
- Create: `tests/test_shopping_list.py`

**Interfaces:**
- Produces:
  - `SNACK = "snack"`
  - `load_grid(path) -> (front, grid)`; `grid` is `[(day, slot, value)]` with the 28 meal entries plus `(day, "snack", slug)` for each day carrying one. Raises `Failure` on a missing meal Slot or `snack: eaten-out`.
  - `check_makes(recipes: dict[slug, front]) -> None`; raises `Failure` listing every violation.
  - `day_macros(grid, recipes) -> {day: {"protein_g": float, "kcal": float, "snacks": [slug, ...]}}` for all 7 `DAYS` (Monday first). Skips any value not in `recipes` (covers `eaten-out`). Rounds to 1 decimal. `snacks` lists, in grid order, each batch contributing to that day.

- [ ] **Step 1: Write the failing tests** — `tests/test_shopping_list.py`:

```python
#!/usr/bin/env python3
"""Tests for bin/shopping-list.py's grid, makes and day_macros rules.

Run: .venv/bin/python tests/test_shopping_list.py
"""

import importlib.util
import os
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "shopping_list", os.path.join(ROOT, "bin", "shopping-list.py"))
sl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sl)

MEALS = {"breakfast": "oats", "lunch": "wrap", "dinner": "chilli", "pudding": "mousse"}

RECIPES = {
    "oats": {"slot": "breakfast", "macros": {"protein_g": 30, "kcal": 400},
             "ingredients": [{"ingredient": "oats", "qty": 80, "unit": "g"}]},
    "wrap": {"slot": "lunch", "macros": {"protein_g": 45, "kcal": 380}, "ingredients": []},
    "chilli": {"slot": "dinner", "macros": {"protein_g": 50, "kcal": 730}, "ingredients": []},
    "mousse": {"slot": "pudding", "macros": {"protein_g": 12, "kcal": 155}, "ingredients": []},
    "bar": {"slot": "snack", "makes": 8, "macros": {"protein_g": 10, "kcal": 150},
            "ingredients": [{"ingredient": "oats", "qty": 200, "unit": "g"}]},
}


def grid_file(days):
    """A Plan file holding `days`, as YAML the way Plan mode writes it."""
    lines = ["---", "days:"]
    for day, slots in days.items():
        lines.append(f"  {day}:")
        lines += [f"    {slot}: {'' if v is None else v}" for slot, v in slots.items()]
    handle = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
    handle.write("\n".join(lines + ["---", ""]))
    handle.close()
    return handle.name


def week(**extra):
    """Seven full meal days; keyword args add or override a day's slots."""
    days = {day: dict(MEALS) for day in sl.DAYS}
    for day, slots in extra.items():
        days[day].update(slots)
    return days


class Grid(unittest.TestCase):
    def load(self, days):
        path = grid_file(days)
        try:
            return sl.load_grid(path)[1]
        finally:
            os.unlink(path)

    def test_a_grid_without_snacks_is_the_28_meal_slots(self):
        self.assertEqual(len(self.load(week())), 28)

    def test_a_snack_is_one_extra_entry_on_its_day(self):
        grid = self.load(week(wednesday={"snack": "bar"}))
        self.assertEqual(len(grid), 29)
        self.assertIn(("wednesday", "snack", "bar"), grid)

    def test_an_empty_snack_is_no_snack(self):
        self.assertEqual(len(self.load(week(wednesday={"snack": None}))), 28)

    def test_a_missing_meal_slot_still_fails(self):
        days = week()
        del days["friday"]["lunch"]
        with self.assertRaisesRegex(sl.Failure, "friday/lunch"):
            self.load(days)

    def test_a_snack_never_reads_eaten_out(self):
        with self.assertRaisesRegex(sl.Failure, "snack"):
            self.load(week(tuesday={"snack": sl.EATEN_OUT}))


class Makes(unittest.TestCase):
    def test_a_snack_with_makes_passes(self):
        sl.check_makes({"bar": RECIPES["bar"]})

    def test_a_snack_without_makes_fails(self):
        bare = dict(RECIPES["bar"]); del bare["makes"]
        with self.assertRaisesRegex(sl.Failure, "bar"):
            sl.check_makes({"bar": bare})

    def test_a_non_positive_makes_fails(self):
        for bad in (0, -2, 2.5, "8"):
            with self.subTest(makes=bad), self.assertRaises(sl.Failure):
                sl.check_makes({"bar": dict(RECIPES["bar"], makes=bad)})

    def test_makes_on_a_meal_fails(self):
        with self.assertRaisesRegex(sl.Failure, "oats"):
            sl.check_makes({"oats": dict(RECIPES["oats"], makes=4)})


class Shopping(unittest.TestCase):
    def test_a_snack_slot_buys_one_whole_batch(self):
        grid = [("monday", "breakfast", "oats"), ("wednesday", "snack", "bar")]
        totals, _, _ = sl.aggregate(grid, RECIPES)
        self.assertEqual(totals["oats"], 280)

    def test_two_bakes_buy_two_batches(self):
        grid = [("monday", "snack", "bar"), ("thursday", "snack", "bar")]
        self.assertEqual(sl.aggregate(grid, RECIPES)[0]["oats"], 400)


def meals_only(day):
    return [(day, slot, slug) for slot, slug in MEALS.items()]


class DayMacros(unittest.TestCase):
    MEAL_DAY = {"protein_g": 137.0, "kcal": 1665.0}

    def test_a_week_of_meals_sums_each_day(self):
        grid = [entry for day in sl.DAYS for entry in meals_only(day)]
        out = sl.day_macros(grid, RECIPES)
        self.assertEqual(list(out), sl.DAYS)
        for day in sl.DAYS:
            self.assertEqual(out[day], dict(self.MEAL_DAY, snacks=[]))

    def test_eaten_out_adds_nothing(self):
        out = sl.day_macros([("monday", "dinner", sl.EATEN_OUT)], RECIPES)
        self.assertEqual(out["monday"], {"protein_g": 0.0, "kcal": 0.0, "snacks": []})

    def test_a_wednesday_bake_spreads_over_wednesday_to_sunday(self):
        out = sl.day_macros([("wednesday", "snack", "bar")], RECIPES)
        for day in ("monday", "tuesday"):
            self.assertEqual(out[day], {"protein_g": 0.0, "kcal": 0.0, "snacks": []})
        for day in ("wednesday", "thursday", "friday", "saturday", "sunday"):
            self.assertEqual(out[day], {"protein_g": 5.7, "kcal": 85.7, "snacks": ["bar"]})

    def test_a_sunday_bake_reaches_sunday_only(self):
        out = sl.day_macros([("sunday", "snack", "bar")], RECIPES)
        self.assertEqual([d for d in sl.DAYS if out[d]["snacks"]], ["sunday"])

    def test_overlapping_bakes_add(self):
        out = sl.day_macros([("monday", "snack", "bar"), ("wednesday", "snack", "bar")],
                            RECIPES)
        self.assertEqual(out["tuesday"]["protein_g"], 5.7)
        self.assertEqual(out["wednesday"]["protein_g"], 11.4)
        self.assertEqual(out["wednesday"]["snacks"], ["bar", "bar"])

    def test_a_snack_slot_is_spread_by_its_slot_not_the_recipes(self):
        """A Slot decides how a Recipe counts: a bar eaten as Monday's pudding
        is a meal, so it counts once and does not spread."""
        out = sl.day_macros([("monday", "pudding", "bar")], RECIPES)
        self.assertEqual(out["monday"]["protein_g"], 10.0)
        self.assertEqual(out["tuesday"]["protein_g"], 0.0)

    def test_an_unknown_slug_adds_nothing(self):
        out = sl.day_macros([("monday", "dinner", "gone")], RECIPES)
        self.assertEqual(out["monday"]["kcal"], 0.0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run, verify failure**

Run: `.venv/bin/python tests/test_shopping_list.py`
Expected: errors — `AttributeError: ... no attribute 'check_makes'` / `'day_macros'`, and `test_a_snack_is_one_extra_entry_on_its_day` failing on length 28. (`test_a_snack_slot_buys_one_whole_batch` passes already — `aggregate` is unchanged by design.)

- [ ] **Step 3: Implement** — in `bin/shopping-list.py`:

After `EATEN_OUT = "eaten-out"`:

```python
# The one optional Slot: a batch baked on the day it sits in and eaten across
# the week. A day without one omits the key. Spec 2026-10-11-snack-slot-design.
SNACK = "snack"
```

Replace `load_grid`'s docstring and add the snack read inside the day loop, after the `for slot in SLOTS:` loop (still inside `for day in DAYS:`):

```python
def load_grid(path):
    """Return the 28 meal Slots, plus any day's snack, as (day, slot, value).
    Hard-fails on an incomplete grid; a snack is optional but never eaten-out."""
```

```python
        snack = entry.get(SNACK)
        if snack == EATEN_OUT:
            raise Failure(f"{path}: {day}/snack is eaten-out -- omit the key instead")
        if snack:
            grid.append((day, SNACK, snack))
```

After `check_rule`:

```python
def check_makes(recipes):
    """A snack says how many servings its batch makes; nothing else does."""
    bad = []
    for slug, recipe in sorted(recipes.items()):
        makes = recipe.get("makes")
        if recipe.get("slot") == SNACK:
            if type(makes) is not int or makes < 1:
                bad.append(f"{slug}: a snack needs makes: <servings per batch>, got {makes!r}")
        elif "makes" in recipe:
            bad.append(f"{slug}: makes: belongs on a snack only")
    if bad:
        raise Failure("makes: rule violated:\n  " + "\n  ".join(bad))


def day_macros(grid, recipes):
    """Per person, per day: the meals, plus each snack batch's share.

    A batch baked on day D is assumed eaten evenly over D..D+6 by 2 people, so
    each of those days gets makes / 2 x per-serving macros / 7. Days past this
    Plan's Sunday are not carried into the next one. A Slot decides how a
    Recipe counts, not the Recipe's own slot: field.
    """
    out = {day: {"protein_g": 0.0, "kcal": 0.0, "snacks": []} for day in DAYS}
    for day, slot, value in grid:
        recipe = recipes.get(value)
        if recipe is None:
            continue  # eaten-out, or a slug the caller could not resolve
        macros = recipe.get("macros") or {}
        if slot == SNACK:
            share, days = recipe["makes"] / 2 / 7, DAYS[DAYS.index(day):]
        else:
            share, days = 1, [day]
        for d in days:
            out[d]["protein_g"] += share * float(macros.get("protein_g") or 0)
            out[d]["kcal"] += share * float(macros.get("kcal") or 0)
            if slot == SNACK:
                out[d]["snacks"].append(value)
    for totals in out.values():
        totals["protein_g"] = round(totals["protein_g"], 1)
        totals["kcal"] = round(totals["kcal"], 1)
    return out
```

In `main`, after `check_rule(recipes, pins)`:

```python
    check_makes(recipes)
```

- [ ] **Step 4: Run, verify pass**

Run: `.venv/bin/python tests/test_shopping_list.py && .venv/bin/python bin/shopping-list.py Plans/2026-10-05.md > /dev/null && echo ok`
Expected: all tests OK, then `ok` (a real Plan still generates).

- [ ] **Step 5: Commit**

```bash
git add bin/shopping-list.py tests/test_shopping_list.py
git commit -m "Read an optional snack Slot and spread its batch over the week"
```

---

### Task 2: `bin/browse.py` sums days with `day_macros`

**Files:**
- Modify: `bin/browse.py` (imports, delete `day_totals`, `load_all`, `build_payload`, `main`'s `__main__` handler)
- Modify: `tests/test_browse.py` (`DayTotals` class, `Plans` class, new `Snacks` class)
- Regenerate: `index.html`

**Interfaces:**
- Consumes: `sl.day_macros`, `sl.check_makes`, `sl.Failure`, `sl.SNACK` from Task 1.
- Produces: module attribute `browse.sl` (the loaded shopping-list module); each recipe row gains `"makes": int | None`; each plan row's `totals[day]` gains `"snacks": [slug, ...]` (keys `protein_g`, `kcal`, `snacks`, `flags`, `cooked`).

- [ ] **Step 1: Write the failing tests** — in `tests/test_browse.py`:

Replace the whole `DayTotals.test_sums_a_days_four_slots_from_the_recipes` method with:

```python
    def test_sums_a_days_four_slots_from_the_recipes(self):
        thursday = plan_payload([{"slug": "2026-09-14", "title": "t",
                                  "days": {"thursday": WEEK_DAYS["thursday"]}}])[0]
        self.assertEqual(thursday["totals"]["thursday"]["protein_g"], 140.0)
        self.assertEqual(thursday["totals"]["thursday"]["kcal"], 1705.0)
```

Add `"bar"` to the `RECIPES` fixture dict (after `"mousse"`):

```python
    "bar": {"slot": "snack", "makes": 8, "macros": {"protein_g": 10, "kcal": 150}, "tags": []},
```

In `AgainstTheRealRepo.test_every_plan_fills_all_twenty_eight_slots`, count meal Slots only, so the first real Plan with a snack does not break it:

```python
            filled = [s for slots in plan["days"].values()
                      for slot, s in slots.items() if s and slot != "snack"]
```

Add after the `Plans` class:

```python
class Snacks(unittest.TestCase):
    def setUp(self):
        days = {day: dict(slots) for day, slots in WEEK_DAYS.items()}
        days["wednesday"]["snack"] = "bar"
        self.plan = {"slug": "2026-09-14", "title": "Week of 2026-09-14", "days": days}

    def test_payload_totals_are_day_macros(self):
        grid = [(d, s, v) for d, slots in self.plan["days"].items() for s, v in slots.items()]
        want = browse.sl.day_macros(grid, RECIPES)
        got = plan_payload([self.plan])[0]["totals"]
        for day in browse.DAYS:
            self.assertEqual({k: got[day][k] for k in ("protein_g", "kcal", "snacks")},
                             want[day])

    def test_a_bake_adds_its_share_from_its_day_on(self):
        totals = plan_payload([self.plan])[0]["totals"]
        self.assertEqual(totals["tuesday"]["snacks"], [])
        self.assertEqual(totals["thursday"]["snacks"], ["bar"])
        self.assertEqual(totals["thursday"]["protein_g"], 145.7)

    def test_a_snack_is_not_a_cooked_meal(self):
        self.assertEqual(plan_payload([self.plan])[0]["cooked"], 28)
        self.assertEqual(plan_payload([self.plan])[0]["totals"]["wednesday"]["cooked"], 4)

    def test_a_week_with_no_snack_sums_as_before(self):
        del self.plan["days"]["wednesday"]["snack"]
        totals = plan_payload([self.plan])[0]["totals"]
        self.assertEqual(totals["thursday"]["protein_g"], 140.0)
        self.assertEqual(totals["thursday"]["kcal"], 1705.0)

    def test_a_snack_row_carries_makes(self):
        rows = {r["slug"]: r for r in browse.build_payload({
            "recipes": RECIPES, "plans": [], "pins": {}, "bands": {},
            "goals": browse.DEFAULT_GOALS})["recipes"]}
        self.assertEqual(rows["bar"]["makes"], 8)
        self.assertIsNone(rows["mousse"]["makes"])

    def test_the_page_refuses_a_snack_without_makes(self):
        with tempfile.TemporaryDirectory() as root:
            for name in ("Recipes", "Plans"):
                os.mkdir(os.path.join(root, name))
            for name, text in {
                "Recipes/bar.md": "---\ntitle: Bar\nslot: snack\nmacros: {protein_g: 1, kcal: 1}\n---\n",
                "PINS.md": "```yaml\n{}\n```\n",
                "GOALS.md": GOALS,
            }.items():
                with open(os.path.join(root, name), "w") as handle:
                    handle.write(text)
            with self.assertRaisesRegex(browse.sl.Failure, "bar"):
                browse.load_all(root)
```

- [ ] **Step 2: Run, verify failure**

Run: `.venv/bin/python tests/test_browse.py 2>&1 | tail -5`
Expected: errors — `AttributeError: module 'browse' has no attribute 'sl'`, `KeyError: 'snacks'`/`'makes'`.

- [ ] **Step 3: Implement** — in `bin/browse.py`:

Add `import importlib.util` to the imports (alphabetical, after `import glob`), and after `class Failure`:

```python
# The shopping list owns the grid's rules -- the snack spread and the makes:
# check -- so the page reads them from there rather than keeping a second copy.
_spec = importlib.util.spec_from_file_location(
    "shopping_list", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "shopping-list.py"))
sl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sl)
```

Delete the whole `def day_totals(slots, recipes):` function.

In `load_all`, load recipes once and check them:

```python
def load_all(root):
    goals_text = read(os.path.join(root, "GOALS.md"))
    recipes = load_recipes(root)
    sl.check_makes(recipes)
    return {
        "recipes": recipes,
```

(the rest of the dict unchanged.)

In `build_payload`'s `recipe_rows.append({...})`, after `"kcal": macros.get("kcal"),`:

```python
            # Servings per batch, on a snack only. VOCABULARY.md.
            "makes": recipe.get("makes"),
```

In `build_payload`'s plan loop, replace from `totals, cooked = {}, 0` through `totals[day] = summed` with:

```python
        totals, cooked = {}, 0
        grid = [(day, slot, value) for day, slots in plan["days"].items()
                for slot, value in slots.items() if value]
        summed_week = sl.day_macros(grid, recipes)
        for day in DAYS:
            slots = plan["days"].get(day, {})
            at_home = sum(1 for slot in SLOTS
                          if slots.get(slot) not in (None, EATEN_OUT))
            cooked += at_home
            summed = summed_week[day]
            # A day nobody cooked misses both goals trivially. Flagging it would
            # report a night out as a nutritional failure.
            summed["flags"] = goal_flags(summed, data["goals"]) if at_home else []
            summed["cooked"] = at_home
            totals[day] = summed
```

In the `if __name__ == "__main__":` block, catch both failures:

```python
    except (Failure, sl.Failure) as exc:
```

- [ ] **Step 4: Run, verify pass, regenerate**

Run: `.venv/bin/python tests/test_browse.py 2>&1 | tail -3 && .venv/bin/python bin/browse.py && .venv/bin/python bin/browse.py --check && git diff --stat index.html`
Expected: `OK`; `index.html is up to date`; the `index.html` diff is payload only (new `"makes": null` on every recipe, `"snacks": []` in every day total) — no total changes, since no Plan holds a snack.

- [ ] **Step 5: Commit**

```bash
git add bin/browse.py tests/test_browse.py index.html
git commit -m "Sum a Plan's days with the shopping list's day_macros"
```

---

### Task 3: The page shows snacks

**Files:**
- Modify: `bin/browse.py` — `TEMPLATE`'s `recipeList`, `recipeDetail`, `dayBlock`
- Modify: `tests/test_browse.py` — one `GeneratedPage`-style check
- Regenerate: `index.html`

**Interfaces:**
- Consumes: recipe rows' `makes`, totals' `snacks` (Task 2).
- Produces: nothing new for later tasks.

- [ ] **Step 1: Write the failing test** — add to `tests/test_browse.py`, after the `Snacks` class:

```python
class SnackPage(unittest.TestCase):
    """The page's snack markup, rendered from a fixture payload."""

    def test_the_recipe_list_groups_snacks_after_puddings(self):
        self.assertIn("D.slots.concat('snack').map(slot =>", browse.TEMPLATE)

    def test_a_day_names_the_bakes_in_its_totals(self):
        self.assertIn("incl. snack share from", browse.TEMPLATE)
```

- [ ] **Step 2: Run, verify failure**

Run: `.venv/bin/python tests/test_browse.py SnackPage`
Expected: 2 failures (`not found in`).

- [ ] **Step 3: Implement** — in `TEMPLATE`:

`recipeList`: the groups line becomes

```js
  const groups = D.slots.concat('snack').map(slot => [slot, sorted(hits.filter(r => r.slot === slot))])
```

and the row's `meta` span gains the batch size first — replace `${[star(r.rating), r.effort ? ...` with `${[r.makes ? 'makes ' + r.makes : '', star(r.rating), r.effort ? ...` (the array is already `.filter(Boolean)`ed).

`recipeDetail`: replace the note after the macros table

```js
      <p class="note">Serves 2. Bands guide, they do not gate — the goals are checked
        by summing a day, not by policing a Recipe.</p></section>
```

with

```js
      <p class="note">${r.makes
        ? `Makes ${r.makes} · macros per serving · quantities for the whole batch.
           Baked on one day, its share counts toward each of the next seven.`
        : 'Serves 2.'} Bands guide, they do not gate — the goals are checked
        by summing a day, not by policing a Recipe.</p></section>
```

`dayBlock`: the `cells` line maps over `D.slots.concat('snack')` and skips an absent snack:

```js
  const cells = D.slots.concat('snack').map(s => {
    const value = p.days[day][s];
    if (s === 'snack' && !value) return '';
```

(rest of the map body unchanged). Then after `const stats = ...;`, before `return`:

```js
  /* A bake's share lands on the next seven days, so a day can carry a snack it
     did not bake. Name them, or the total reads higher than its meals. */
  const bakes = [...new Set(t.snacks || [])].map(s => esc((byslug[s] || {}).title || s));
  const snackNote = t.cooked && bakes.length
    ? `<p class="note">incl. snack share from ${bakes.join(', ')}</p>` : '';
```

and the return's `${stats}<dl>${cells}</dl></div>` becomes `${stats}<dl>${cells}</dl>${snackNote}</div>`.

- [ ] **Step 4: Run, verify pass, regenerate**

Run: `.venv/bin/python tests/test_browse.py 2>&1 | tail -3 && .venv/bin/python bin/browse.py && .venv/bin/python bin/browse.py --check`
Expected: `OK`, `index.html is up to date`.

Then eyeball it once with a throwaway snack (not committed): write `Recipes/zz-test-bar.md` (`slot: snack`, `makes: 8`, `macros: {protein_g: 10, kcal: 150}`, one ingredient, one method step), add `snack: zz-test-bar` to `wednesday` in a **copy** of the latest Plan saved as `Plans/2099-01-05.md`, run `bin/browse.py`, open `index.html` with Playwright's Chromium (`executablePath: '/opt/pw-browsers/chromium'`) at `#recipes` and `#plan/2099-01-05`, and screenshot: a *Snack* group after *Pudding* with `makes 8`; Wednesday lists the snack; Thursday's note reads "incl. snack share from …". Then `rm Recipes/zz-test-bar.md Plans/2099-01-05.md && .venv/bin/python bin/browse.py && git status --short` — only the intended files may show.

- [ ] **Step 5: Commit**

```bash
git add bin/browse.py tests/test_browse.py index.html
git commit -m "Show snacks on the browse page: a Snack group, a bake line, the share note"
```

---

### Task 4: Plan mode's skippable snack step

**Files:**
- Modify: `bin/browse.py` — `TEMPLATE`'s Plan-mode block (`PLAN_SEQ`, `planDone`, `planYaml`, `planSet`, `weekRows`, `checkoutView`, `renderDrawer`)
- Modify: `tests/test_browse.py` — `WeekRows` fixture/cases, new `PlanYaml` node class
- Regenerate: `index.html`

**Interfaces:**
- Consumes: nothing new.
- Produces: `planYaml(plan, week, slots)` — pure, returns the `days:` block string; `weekRows(plan, week, slots, titles)` — unchanged signature, appends `['snack', title]` to a day that has a snack.

- [ ] **Step 1: Write the failing tests** — in `tests/test_browse.py`:

Extend `ROW_PLAN` with a snack on Monday: add `"monday.snack": "oats"` to the dict. Add to `WeekRows`:

```python
    def test_a_day_with_a_snack_lists_it_after_its_meals(self):
        self.assertEqual(self.rows[0]["slots"][4], ["snack", "Overnight Oats"])

    def test_a_day_without_a_snack_lists_only_its_meals(self):
        self.assertEqual(len(self.rows[1]["slots"]), 4)
```

and change `test_every_day_lists_every_slot_in_order` to compare the first four only:

```python
            self.assertEqual([s for s, _ in row["slots"]][:4], ROW_SLOTS)
```

Add a new class after `WeekRows`, in the same lift-and-run style:

```python
PLAN_YAML = re.compile(r"function planYaml\(plan, week, slots\)\{.*?\n\}", re.S)


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class PlanYaml(unittest.TestCase):
    """Checkout's days: block. A snack line only on a day that baked one."""

    @classmethod
    def setUpClass(cls):
        fn = PLAN_YAML.search(browse.TEMPLATE)
        assert fn, "planYaml is no longer in TEMPLATE"
        plan = {f"{d}.{s}": "x" for d in ("monday", "tuesday") for s in ROW_SLOTS}
        plan["tuesday.snack"] = "bar"
        script = fn.group(0) + "\nconsole.log(JSON.stringify(planYaml(%s, %s, %s)));\n" % (
            json.dumps(plan), json.dumps(["monday", "tuesday"]), json.dumps(ROW_SLOTS))
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as handle:
            handle.write(script)
            path = handle.name
        try:
            out = subprocess.run([shutil.which("node"), path], check=True,
                                 capture_output=True, text=True).stdout
        finally:
            os.unlink(path)
        cls.yaml = json.loads(out)

    def test_a_snack_line_follows_pudding_on_its_day(self):
        self.assertIn("    pudding: x\n    snack: bar\n", self.yaml)

    def test_a_day_without_a_snack_writes_no_snack_line(self):
        self.assertEqual(self.yaml.count("snack:"), 1)

    def test_the_block_loads_as_the_grid_shopping_list_reads(self):
        import yaml
        days = yaml.safe_load(self.yaml)["days"]
        self.assertEqual(days["tuesday"]["snack"], "bar")
        self.assertNotIn("snack", days["monday"])
```

- [ ] **Step 2: Run, verify failure**

Run: `.venv/bin/python tests/test_browse.py WeekRows PlanYaml`
Expected: `AssertionError: planYaml is no longer in TEMPLATE`, and the two new `WeekRows` cases fail.

- [ ] **Step 3: Implement** — in `TEMPLATE`'s Plan-mode block:

```js
/* Each day walks its four meals, then its snack -- the one optional Slot, and
   Skip is its expected answer. Progress and Checkout count the meals alone. */
const PLAN_SEQ = WEEK.flatMap(day => D.slots.concat('snack').map(slot => [day, slot]));
const MEAL_COUNT = PLAN_SEQ.filter(([, slot]) => slot !== 'snack').length;
```

```js
const planDone = () => PLAN_SEQ.filter(pair => pair[1] !== 'snack' && plan[planKey(pair)]).length;
```

Replace `planYaml` with a pure version:

```js
/* The Plan grid's own frontmatter shape -- two-space YAML, every meal Slot
   valued, a skipped one spelled `eaten-out`, and a snack line only on a day
   that bakes one. VOCABULARY.md, The Plan grid. */
function planYaml(plan, week, slots){
  return 'days:\n' + week.map(day => '  ' + day + ':\n' +
    slots.concat(plan[day + '.snack'] ? ['snack'] : [])
      .map(s => '    ' + s + ': ' + plan[day + '.' + s]).join('\n')
  ).join('\n') + '\n';
}
```

and its one caller in `checkoutView` becomes `${esc(planYaml(plan, WEEK, D.slots))}`.

`planSet` — a skipped snack is no key at all:

```js
function planSet(value){
  if (cursor >= PLAN_SEQ.length) return;
  if (value) plan[planKey(PLAN_SEQ[cursor])] = value;
  else delete plan[planKey(PLAN_SEQ[cursor])];
  planNext();
}
```

`weekRows` — a snack row only where one is set:

```js
function weekRows(plan, week, slots, titles){
  return week.map(day => ({day, slots: slots.concat(plan[day + '.snack'] ? ['snack'] : [])
    .map(slot => {
      const v = plan[day + '.' + slot];
      return [slot, !v ? '—' : v === 'eaten-out' ? 'skipped' : titles[v] || v];
    })}));
}
```

`renderDrawer`: `${done} / ${PLAN_SEQ.length}` → `${done} / ${MEAL_COUNT}`; the Checkout button's `done < PLAN_SEQ.length` → `done < MEAL_COUNT`; the Skip button's handler becomes

```js
  if (at) document.getElementById('planskip').onclick = () =>
    planSet(at[1] === 'snack' ? null : 'eaten-out');
```

and when the cursor is on a snack, label the step so Skip reads as the default — in `here`, after `<b>${cap(at[0])} ${at[1]}</b>` add `${at[1] === 'snack' ? ' <span class="note">— optional, Skip if nothing is baked</span>' : ''}`.

`checkoutView`'s lede: after `It buys nothing.` add ` A day that bakes a snack gets a <code>snack:</code> line; the rest have none.`

- [ ] **Step 4: Run, verify pass, regenerate**

Run: `.venv/bin/python tests/test_browse.py 2>&1 | tail -3 && .venv/bin/python bin/browse.py && .venv/bin/python bin/browse.py --check`
Expected: `OK`, `index.html is up to date`.

Then drive it once in Chromium (Playwright, `executablePath: '/opt/pw-browsers/chromium'`) against `index.html`: enter Plan mode, click a Recipe for each of Monday's four meals, confirm the drawer reads `4 / 28` and names `Monday snack — optional`, click Skip, fill the remaining 24 meals (any Recipe), confirm Checkout is enabled and the textarea's YAML holds no `snack:` line. Then Back into one snack step, pick a snack Recipe if the pool has one (else skip this half), Checkout, and confirm exactly one `snack:` line. Feed that YAML into a temp Plan and run `bin/shopping-list.py` on it — exit 0.

- [ ] **Step 5: Commit**

```bash
git add bin/browse.py tests/test_browse.py index.html
git commit -m "Add a skippable snack step to Plan mode; Checkout writes it only when set"
```

---

### Task 5: The prose

**Files:**
- Modify: `VOCABULARY.md`, `CONTEXT.md`, `CLAUDE.md`, `.claude/skills/plan-the-week/SKILL.md`, `.claude/skills/new-recipe/SKILL.md`, `.scratch/meal-planning-system/map.md`, `docs/superpowers/specs/2026-10-11-snack-slot-design.md` (status line)
- Create: `.scratch/meal-planning-system/issues/26-the-snack-slot.md`

**Interfaces:** none; prose only. Each skill snippet must run against the Task 1 code.

- [ ] **Step 1: `VOCABULARY.md`**
  - `slot` row values: add `` `snack` ``.
  - `protein` row: `one, or absent on a pudding or snack`.
  - New row after `retired`: `` | `makes` | a positive integer, required on a `snack`, absent otherwise | servings per batch | ``
  - *The Plan grid*: after the `eaten-out` bullet's paragraph, add: "**`snack` is the one optional Slot.** A day may also hold `snack: <slug>` — a batch baked that day, bought once, and counted in day totals as an even share over the seven days from it. A day with no snack omits the key; `snack: eaten-out` is rejected. So a grid is 28 meal Slots plus up to seven snacks."
  - *Notes on three fields* gets a paragraph: "**A snack's quantities are for the whole batch and its `macros` per serving** — the one exception to *Serves 2*. `makes` is what lets the shopping list buy one batch and the day totals spread it."

- [ ] **Step 2: `CONTEXT.md`** *Slot*: "breakfast, lunch, dinner, pudding" → "breakfast, lunch, dinner, pudding, and the optional **snack** — a batch baked on the day it sits in and eaten across the week."

- [ ] **Step 3: `CLAUDE.md`**
  - *Serves 2* line: append " The one exception is a **snack**: a batch Recipe carries `makes:`, whole-batch quantities and per-serving macros."
  - Finish-list step 2: append a sibling command — `` `.venv/bin/python tests/test_shopping_list.py` `` — and update the counts to what `tests/test_browse.py` and `tests/test_shopping_list.py` actually report now (run both; write the numbers, and the node-shelling count from `grep -c "subprocess.run" ` is **not** the count — count the test methods in node-gated classes).

- [ ] **Step 4: `plan-the-week` skill**
  - Step 2's grid example: after `breakfast: <slug>` / `...`, show `      snack: <slug>   # optional; only on a day that bakes one`.
  - Step 4's snippet becomes:

```bash
.venv/bin/python - Plans/<Monday>.md <<'PY'
import sys; sys.path.insert(0, 'bin')
sl = __import__('shopping-list')
front, grid = sl.load_grid(sys.argv[1])
totals = sl.day_macros(grid, sl.load_recipes('.', grid))
out = {d: sum(1 for day, s, v in grid if day == d and v == sl.EATEN_OUT) for d in sl.DAYS}
for d in sl.DAYS:
    p, k, snacks = totals[d]['protein_g'], totals[d]['kcal'], totals[d]['snacks']
    note = (f"  {out[d]} Slot(s) eaten out -- not judged" if out[d] else
            ("  UNDER the ~120g floor" if p < 120 else "")
            + ("  OVER the ~1800 kcal ceiling" if k > 1800 else ""))
    bakes = f"  (incl. snack share: {', '.join(sorted(set(snacks)))})" if snacks else ""
    print(f"{d:<10} ~{p:g}g protein  ~{k:g} kcal{note}{bakes}")
PY
```

  - *The grid stays whole*: add "The one exception is `snack`: optional, absent on a day that bakes nothing, and never `eaten-out`."
  - Verify: run the new snippet against `Plans/2026-10-05.md`; the figures must equal the old snippet's (`git show HEAD:.claude/skills/plan-the-week/SKILL.md`) for every day.

- [ ] **Step 5: `new-recipe` skill**
  - Step 2: add "Snacks carry no protein either: `grep -l '^slot: snack' Recipes/*.md`."
  - Step 4: "`protein` omitted on a pudding" → "on a pudding or snack"; after the template, add: "A **snack** adds `makes: 8` after `slot:` — servings per batch — and its `qty` values are for the **whole batch**, its `macros` per serving."
  - Step 5's check: `V['slot']` gains `'snack'`; the pudding branch becomes `if front.get('slot') in ('pudding', 'snack'):` with message `f"a {front.get('slot')} carries no protein"`; and before `steps = ...` add:

```python
   try:
       sl.check_makes({slug: front})
   except sl.Failure as e:
       bad += str(e).splitlines()[1:]
```

  - *The bar* table: add `| Snack | measured once a few exist | — | — |`.
  - Verify: run the check against one existing Recipe (`Recipes/brownie-bar.md`) — still `clean`.

- [ ] **Step 6: Ticket 26 and the map** — create `.scratch/meal-planning-system/issues/26-the-snack-slot.md` in ticket 25's shape:

```markdown
# The Snack Slot

Type: decision
Status: resolved
Blocked by: —

## Question

Batch bakes — mostly 8 servings — are cooked on the odd day and eaten through
the week. A Plan had nowhere to put one: a meal Slot buys a batch per Slot and
counts the whole batch's macros on one day.

## Answer

**A fifth, optional Slot, `snack`, meaning the day the batch is baked.** It
buys one batch; its macros spread evenly over the seven days from it, clipped
at the Plan's Sunday, overlapping batches adding. A snack Recipe carries
`makes:`, whole-batch quantities and per-serving macros — the one exception to
Serves 2. The full design is
[the snack Slot spec](../../../docs/superpowers/specs/2026-10-11-snack-slot-design.md).

### What changed

- `bin/shopping-list.py`: the grid's optional `snack:` key, `check_makes`, and
  `day_macros` — the one place the spread is computed.
- `bin/browse.py`: reads day totals from `day_macros` (its own `day_totals` is
  gone), a Snack group, a snack line per day, and a skippable snack step in
  Plan mode.
- `VOCABULARY.md`, `CONTEXT.md`, `CLAUDE.md`, `plan-the-week`, `new-recipe`.

### Not done

- No snack Band in `GOALS.md` until a few snacks exist to measure.
- A batch *breakfast* still buys a batch per Slot.
- A late-week bake's spread is not carried into the next Plan.
```

  Add a matching entry to `map.md` after the *Retire Menus* entry: "- [The Snack Slot](issues/26-the-snack-slot.md), settled 11 October 2026: **a fifth, optional Slot for batch bakes**, bought once on its bake day and spread over the next seven days' totals. `day_macros` in `bin/shopping-list.py` becomes the single day-sum both the skill and the page use."

  Spec status line → `Status: implemented — see issues/26-the-snack-slot.md`.

- [ ] **Step 7: Full check, commit, push**

Run: `.venv/bin/python tests/test_shopping_list.py && .venv/bin/python tests/test_browse.py && .venv/bin/python bin/browse.py --check && for p in Plans/*.md; do .venv/bin/python bin/shopping-list.py "$p" > /dev/null || echo "FAIL $p"; done`
Expected: both suites `OK`, `index.html is up to date`, no `FAIL`.

```bash
git add VOCABULARY.md CONTEXT.md CLAUDE.md .claude/skills .scratch docs/superpowers/specs
git commit -m "Record the snack Slot: vocabulary, skills and ticket 26"
git push -u origin claude/coding-session-l82e7v
```
