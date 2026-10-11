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

    def test_a_meal_in_a_snack_slot_spreads_as_two_servings(self):
        """No makes: on a meal, so a snack Slot holding one reads it as one
        serving each -- spread like any bake, never a crash."""
        out = sl.day_macros([("saturday", "snack", "oats")], RECIPES)
        self.assertEqual(out["saturday"]["protein_g"], 4.3)
        self.assertEqual(out["sunday"]["snacks"], ["oats"])

    def test_an_unknown_slug_adds_nothing(self):
        out = sl.day_macros([("monday", "dinner", "gone")], RECIPES)
        self.assertEqual(out["monday"]["kcal"], 0.0)


if __name__ == "__main__":
    unittest.main()
