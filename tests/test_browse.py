#!/usr/bin/env python3
"""Tests for bin/browse.py.

Run: python3 tests/test_browse.py

These exist for one reason above all others: `Orders/*.md` hold real personal
data and `index.html` is committed and published. A redaction that silently
stops redacting is the failure this file is here to catch.
"""

import importlib.util
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "bin", filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


browse = _load("browse", "browse.py")


ORDER = """# Waitrose Order — 11 August 2026

Order number 1000000001. Collected Tuesday 11 August, 10:00am-11:00am, from Riverside, AB1 2CD.

### Bakery

| Line | Item | Size | Qty | Cost |
|---|---|---|---|---|
| 841175 | Light Rye Boule | each | 1 | £2.50 |

### Household

| Line | Item | Size | Qty | Cost |
|---|---|---|---|---|
| 733624 | Ecover Non Bio Washing Liquid 40w | 1.43litre | 1 | £10.50 |

### Toiletries, Health & Beauty

| Line | Item | Size | Qty | Cost |
|---|---|---|---|---|
| 990001 | Example Deodorant Refill | 40g | 1 | £6.00 |

### Cost breakdown

- Item total: £123.29
- Savings: −£0.70
- **Total: £122.59**
"""


class ParseOrder(unittest.TestCase):
    def setUp(self):
        self.order = browse.parse_order(ORDER, "11-august.md")

    def test_reads_the_order_date_from_the_heading(self):
        self.assertEqual(self.order["date"], "11 August 2026")

    def test_reads_an_item_row_into_its_fields(self):
        bakery = [c for c in self.order["categories"] if c["name"] == "Bakery"][0]
        self.assertEqual(
            bakery["items"],
            [{"line": "841175", "item": "Light Rye Boule", "size": "each",
              "qty": 1, "cost": "£2.50"}],
        )

    def test_reads_the_order_total(self):
        self.assertEqual(self.order["total"], "£122.59")


class Redaction(unittest.TestCase):
    def setUp(self):
        self.order = browse.parse_order(ORDER, "11-august.md")
        self.text = browse.json_dump(self.order)

    def test_omits_the_order_number(self):
        self.assertNotIn("1000000001", self.text)

    def test_omits_the_collection_branch_and_postcode(self):
        self.assertNotIn("Riverside", self.text)
        self.assertNotIn("AB1 2CD", self.text)

    def test_omits_the_collection_time_window(self):
        self.assertNotIn("10:00am", self.text)

    def test_omits_the_toiletries_category_entirely(self):
        names = [c["name"] for c in self.order["categories"]]
        self.assertNotIn("Toiletries, Health & Beauty", names)
        self.assertNotIn("Deodorant", self.text)
        self.assertNotIn("990001", self.text)

    def test_keeps_the_household_category(self):
        names = [c["name"] for c in self.order["categories"]]
        self.assertIn("Household", names)
        self.assertIn("Ecover Non Bio Washing Liquid 40w", self.text)


class PiiGuard(unittest.TestCase):
    """browse.py must refuse to emit a page that carries a redacted string."""

    def test_accepts_a_page_with_no_redacted_string(self):
        browse.assert_no_pii("<p>Light Rye Boule</p>", [ORDER])

    def test_rejects_a_page_carrying_an_order_number(self):
        with self.assertRaises(browse.Failure) as caught:
            browse.assert_no_pii("<p>order 1000000001</p>", [ORDER])
        self.assertIn("1000000001", str(caught.exception))

    def test_rejects_a_page_carrying_the_postcode(self):
        with self.assertRaises(browse.Failure):
            browse.assert_no_pii("<p>AB1 2CD</p>", [ORDER])

    def test_rejects_a_page_carrying_a_toiletries_item(self):
        with self.assertRaises(browse.Failure):
            browse.assert_no_pii("<p>Example Deodorant Refill</p>", [ORDER])


GOALS = """## Macro Bands

| Slot | Target protein | Target kcal | Protein range | kcal range |
| --- | --- | --- | --- | --- |
| Breakfast | ~27g | ~420 | 17-32g | 295-490 |
| Lunch | ~45g | ~380 | 43-48g | 330-420 |
| Dinner | ~48g | ~730 | 42-58g | 695-800 |
| Pudding | ~12g | ~155 | 10-20g | 100-250 |
| **Day** | **~132g** | **~1685** | | |
"""

PINS = {
    "greek-yogurt": {"display": "Greek yogurt", "store": "waitrose", "unit": "g",
                     "search_term": "Fage Total 2% Fat Natural Greek Yogurt Large",
                     "line_number": "603600", "staple": False},
    "honey": {"display": "Honey", "store": "soutars", "unit": "g", "staple": True},
}


class Bands(unittest.TestCase):
    def setUp(self):
        self.bands = browse.parse_bands(GOALS)

    def test_reads_a_slots_target_and_range(self):
        self.assertEqual(
            self.bands["dinner"],
            {"protein_target": 48.0, "kcal_target": 730.0,
             "protein_range": [42.0, 58.0], "kcal_range": [695.0, 800.0]},
        )

    def test_ignores_the_day_summary_row(self):
        self.assertEqual(sorted(self.bands), ["breakfast", "dinner", "lunch", "pudding"])

    def test_scores_a_macro_inside_its_band_range(self):
        self.assertEqual(browse.band_score(48, self.bands["dinner"], "protein"), "in")

    def test_scores_a_macro_below_its_band_range(self):
        self.assertEqual(browse.band_score(30, self.bands["dinner"], "protein"), "under")

    def test_scores_a_macro_above_its_band_range(self):
        self.assertEqual(browse.band_score(900, self.bands["dinner"], "kcal"), "over")


class Ingredients(unittest.TestCase):
    def test_annotates_a_pinned_ingredient_with_its_store_and_product(self):
        line = {"ingredient": "greek-yogurt", "qty": 200, "unit": "g", "note": "Fage 2%"}
        self.assertEqual(
            browse.annotate_ingredient(line, PINS),
            {"ingredient": "greek-yogurt", "qty": 200, "unit": "g", "note": "Fage 2%",
             "display": "Greek yogurt", "store": "waitrose", "staple": False,
             "product": "Fage Total 2% Fat Natural Greek Yogurt Large",
             "line": "603600", "pinned": True},
        )

    def test_flags_an_unpinned_ingredient(self):
        line = {"ingredient": "blueberries", "qty": 100, "unit": "g"}
        annotated = browse.annotate_ingredient(line, PINS)
        self.assertFalse(annotated["pinned"])
        self.assertIsNone(annotated["store"])
        self.assertEqual(annotated["display"], "Blueberries")

    def test_marks_a_staple(self):
        line = {"ingredient": "honey", "qty": 10, "unit": "g"}
        self.assertTrue(browse.annotate_ingredient(line, PINS)["staple"])


RECIPES = {
    "sausage-hash": {"slot": "breakfast", "protein": "sausage",
                     "macros": {"protein_g": 30, "kcal": 400}, "tags": []},
    "egg-scramble": {"slot": "breakfast", "protein": "egg",
                     "macros": {"protein_g": 25, "kcal": 380}, "tags": []},
    "tofu-pan": {"slot": "lunch", "protein": "tofu",
                 "macros": {"protein_g": 45, "kcal": 380}, "tags": []},
    "chicken-pan": {"slot": "lunch", "protein": "chicken",
                    "macros": {"protein_g": 46, "kcal": 390}, "tags": []},
    "bream": {"slot": "dinner", "protein": "white-fish",
              "macros": {"protein_g": 48, "kcal": 700}, "tags": []},
    "salmon": {"slot": "dinner", "protein": "oily-fish",
               "macros": {"protein_g": 50, "kcal": 730}, "tags": []},
    "steak": {"slot": "dinner", "protein": "beef",
              "macros": {"protein_g": 52, "kcal": 760}, "tags": []},
    "roast-chicken": {"slot": "dinner", "protein": "chicken",
                      "macros": {"protein_g": 50, "kcal": 720}, "tags": []},
    "burger": {"slot": "dinner", "protein": "chicken",
               "macros": {"protein_g": 55, "kcal": 780}, "tags": ["fakeaway"]},
    "mousse": {"slot": "pudding", "macros": {"protein_g": 13, "kcal": 165}, "tags": []},
}

LEGAL_DAYS = {
    "sunday": {"breakfast": "egg-scramble", "lunch": "tofu-pan",
               "dinner": "bream", "pudding": "mousse"},
    "monday": {"breakfast": "egg-scramble", "lunch": "tofu-pan",
               "dinner": "bream", "pudding": "mousse"},
    "tuesday": {"breakfast": "egg-scramble", "lunch": "chicken-pan",
                "dinner": "roast-chicken", "pudding": "mousse"},
    "wednesday": {"breakfast": "egg-scramble", "lunch": "chicken-pan",
                  "dinner": "salmon", "pudding": "mousse"},
    "thursday": {"breakfast": "sausage-hash", "lunch": "tofu-pan",
                 "dinner": "steak", "pudding": "mousse"},
    "friday": {"breakfast": "sausage-hash", "lunch": "tofu-pan",
               "dinner": "burger", "pudding": "mousse"},
    "saturday": {"breakfast": "sausage-hash", "lunch": "chicken-pan",
                 "dinner": "salmon", "pudding": "mousse"},
}


class DayTotals(unittest.TestCase):
    def test_sums_a_days_four_slots_from_the_recipes(self):
        totals = browse.day_totals(LEGAL_DAYS["thursday"], RECIPES)
        self.assertEqual(totals, {"protein_g": 140.0, "kcal": 1705.0})

    def test_a_day_clearing_the_floor_and_the_ceiling_is_flagged_neither_way(self):
        self.assertEqual(browse.goal_flags({"protein_g": 140.0, "kcal": 1685.0}), [])

    def test_flags_a_day_under_the_protein_floor(self):
        self.assertEqual(
            browse.goal_flags({"protein_g": 110.0, "kcal": 1600.0}), ["protein"]
        )

    def test_flags_a_day_over_the_kcal_ceiling(self):
        self.assertEqual(
            browse.goal_flags({"protein_g": 140.0, "kcal": 1900.0}), ["kcal"]
        )


class WeeklyLayout(unittest.TestCase):
    def test_a_legal_week_reports_no_violation(self):
        self.assertEqual(browse.layout_violations(LEGAL_DAYS, RECIPES), [])

    def test_flags_a_breakfast_split_that_is_not_three_sausage_and_four_egg(self):
        days = {d: dict(s) for d, s in LEGAL_DAYS.items()}
        days["saturday"]["breakfast"] = "egg-scramble"
        self.assertIn("breakfast", " ".join(browse.layout_violations(days, RECIPES)))

    def test_flags_a_lunch_week_with_fewer_than_two_of_a_type(self):
        days = {d: dict(s) for d, s in LEGAL_DAYS.items()}
        for day in ("tuesday", "wednesday", "saturday"):
            days[day]["lunch"] = "tofu-pan"
        self.assertIn("chicken", " ".join(browse.layout_violations(days, RECIPES)))

    def test_flags_a_fixed_dinner_on_the_wrong_day(self):
        days = {d: dict(s) for d, s in LEGAL_DAYS.items()}
        days["tuesday"]["dinner"] = "salmon"
        self.assertIn("Tuesday", " ".join(browse.layout_violations(days, RECIPES)))

    def test_flags_a_friday_dinner_that_is_not_a_fakeaway(self):
        days = {d: dict(s) for d, s in LEGAL_DAYS.items()}
        days["friday"]["dinner"] = "roast-chicken"
        self.assertIn("Friday", " ".join(browse.layout_violations(days, RECIPES)))

    def test_leaves_saturday_dinner_free(self):
        days = {d: dict(s) for d, s in LEGAL_DAYS.items()}
        days["saturday"]["dinner"] = "steak"
        self.assertEqual(browse.layout_violations(days, RECIPES), [])


class Orphans(unittest.TestCase):
    def test_names_a_recipe_no_menu_uses(self):
        menus = [{"slug": "menu-1", "days": LEGAL_DAYS}]
        self.assertEqual(browse.orphans(RECIPES, menus), [])

    def test_finds_the_recipe_left_out(self):
        menus = [{"slug": "menu-1", "days": LEGAL_DAYS}]
        recipes = dict(RECIPES)
        recipes["lonely-pudding"] = {"slot": "pudding",
                                     "macros": {"protein_g": 12, "kcal": 150}, "tags": []}
        self.assertEqual(browse.orphans(recipes, menus), ["lonely-pudding"])


class OrderAggregate(unittest.TestCase):
    def setUp(self):
        self.orders = [
            {"date": "11 August 2026", "categories": [
                {"name": "Bakery", "items": [
                    {"line": "841175", "item": "Light Rye Boule", "size": "each",
                     "qty": 1, "cost": "£2.50"}]}]},
            {"date": "25 August 2026", "categories": [
                {"name": "Bakery", "items": [
                    {"line": "841175", "item": "Light Rye Boule", "size": "each",
                     "qty": 2, "cost": "£5.00"}]},
                {"name": "Fresh & Chilled", "items": [
                    {"line": "603600", "item": "Fage Total 2% Fat Natural Greek Yogurt Large",
                     "size": "950g", "qty": 3, "cost": "£18.00"}]}]},
        ]
        self.rows = {r["line"]: r for r in browse.order_aggregate(self.orders, PINS)}

    def test_counts_how_many_orders_an_item_appears_in(self):
        self.assertEqual(self.rows["841175"]["orders"], 2)

    def test_sums_the_quantity_bought_across_orders(self):
        self.assertEqual(self.rows["841175"]["qty"], 3)

    def test_records_the_dates_it_was_bought(self):
        self.assertEqual(self.rows["841175"]["dates"],
                         ["11 August 2026", "25 August 2026"])

    def test_joins_a_bought_line_to_the_pin_that_cites_it(self):
        self.assertEqual(self.rows["603600"]["pinned_as"], "greek-yogurt")

    def test_leaves_an_unpinned_line_as_the_pinning_worklist(self):
        self.assertIsNone(self.rows["841175"]["pinned_as"])



class AgainstTheRealRepo(unittest.TestCase):
    """The pure functions above use fixtures. These read what is actually here."""

    @classmethod
    def setUpClass(cls):
        cls.data = browse.load_all(ROOT)

    def test_default_goals_still_match_goals_md(self):
        goals = browse.parse_nutrient_goals(
            open(os.path.join(ROOT, "GOALS.md"), encoding="utf-8").read())
        self.assertEqual(goals, browse.DEFAULT_GOALS)

    def test_reads_every_recipe_in_the_pool(self):
        on_disk = len([f for f in os.listdir(os.path.join(ROOT, "Recipes"))
                       if f.endswith(".md")])
        self.assertEqual(len(self.data["recipes"]), on_disk)

    def test_a_rated_recipe_carries_its_rating_into_the_payload(self):
        rows = browse.build_payload(self.data)["recipes"]
        rated = {r["slug"]: r["rating"] for r in rows if r["rating"] is not None}
        self.assertTrue(rated, "no Recipe in the pool carries a rating")
        for slug, rating in rated.items():
            self.assertIn(rating, range(1, 6), slug)

    def test_an_unrated_recipe_carries_none_rather_than_a_number(self):
        rows = browse.build_payload(self.data)["recipes"]
        on_disk = browse.load_recipes(ROOT)
        unrated = [r for r in rows if "rating" not in on_disk[r["slug"]]]
        self.assertTrue(unrated, "every Recipe is rated; nothing left to check")
        for row in unrated:
            self.assertIsNone(row["rating"], row["slug"])

    def test_reads_both_menus_as_twenty_eight_filled_slots(self):
        self.assertEqual(len(self.data["menus"]), 2)
        for menu in self.data["menus"]:
            filled = [s for slots in menu["days"].values() for s in slots.values() if s]
            self.assertEqual(len(filled), 28, menu["slug"])

    def test_every_menu_slot_resolves_to_a_recipe(self):
        unresolved = sorted({s for menu in self.data["menus"]
                             for slots in menu["days"].values() for s in slots.values()
                             if s not in self.data["recipes"]})
        self.assertEqual(unresolved, [])

    def test_reads_every_captured_order(self):
        self.assertEqual(len(self.data["orders"]), 4)

    def test_no_captured_order_carries_a_redacted_category(self):
        for order in self.data["orders"]:
            for category in order["categories"]:
                self.assertNotIn(category["name"], browse.REDACTED_CATEGORIES)


class GeneratedPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = browse.load_all(ROOT)
        cls.html = browse.render(cls.data)

    def test_the_page_is_self_contained(self):
        self.assertNotIn("<script src=", self.html)
        self.assertNotIn("<link rel=\"stylesheet\"", self.html)

    def test_the_page_carries_no_redacted_string(self):
        browse.assert_no_pii(self.html, self.data["raw_orders"])

    def test_the_page_inlines_every_recipe_title(self):
        for recipe in self.data["recipes"].values():
            self.assertIn(json.dumps(recipe["title"])[1:-1], self.html)

    def test_the_page_inlines_every_order_date(self):
        for order in self.data["orders"]:
            self.assertIn(order["date"], self.html)


class Search(unittest.TestCase):
    """Both vocabularies are searchable, which is the whole point of PINS.md:
    the Recipe's word and the product's word disagree."""

    @classmethod
    def setUpClass(cls):
        cls.payload = browse.build_payload(browse.load_all(ROOT))
        cls.by = {r["slug"]: r for r in cls.payload["recipes"]}

    def hits(self, term):
        return sorted(r["slug"] for r in self.payload["recipes"]
                      if term.lower() in r["haystack"])

    def test_finds_a_recipe_by_the_word_the_recipe_uses(self):
        self.assertIn("pan-seared-white-fish-with-rice-cooker-lemon-herb-grains-parmesan-asparagus",
                      self.hits("parmesan"))

    def test_finds_the_same_recipe_by_the_word_on_the_shelf(self):
        self.assertEqual(self.hits("parmigiano"), self.hits("parmesan"))

    def test_finds_pine_nuts_by_their_product_name_pine_kernels(self):
        self.assertTrue(self.hits("pine kernels"))

    def test_finds_a_recipe_by_its_method_text(self):
        self.assertIn("eggy-bread", self.hits("whisk"))

    def test_finds_a_recipe_by_an_ingredient_slug(self):
        self.assertTrue(self.hits("greek-yogurt"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
