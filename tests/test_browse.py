#!/usr/bin/env python3
"""Tests for bin/browse.py.

Run: .venv/bin/python tests/test_browse.py

These exist for one reason above all others: `Orders/*.md` hold real personal
data and `index.html` is committed and published. A redaction that silently
stops redacting is the failure this file is here to catch.
"""

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
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

WEEK_DAYS = {
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
        totals = browse.day_totals(WEEK_DAYS["thursday"], RECIPES)
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



def plan_payload(plans):
    """build_payload over fixture Plans, with everything else stubbed empty."""
    return browse.build_payload({
        "recipes": RECIPES, "plans": plans, "pins": {},
        "bands": {}, "goals": browse.DEFAULT_GOALS, "orders": [], "history": [],
    })["plans"]


class Plans(unittest.TestCase):
    def setUp(self):
        days = {day: dict(slots) for day, slots in WEEK_DAYS.items()}
        days["monday"] = {slot: browse.EATEN_OUT for slot in browse.SLOTS}
        days["sunday"]["lunch"] = browse.EATEN_OUT
        self.plan = {"slug": "2026-09-14", "title": "Week of 2026-09-14",
                     "days": days}

    def test_lists_the_latest_week_first(self):
        with tempfile.TemporaryDirectory() as root:
            os.mkdir(os.path.join(root, "Plans"))
            for date in ("2026-08-31", "2026-09-14", "2026-09-07"):
                with open(os.path.join(root, "Plans", date + ".md"), "w") as handle:
                    handle.write("---\ntitle: Week of %s\ndays: {}\n---\n" % date)
            self.assertEqual([p["slug"] for p in browse.load_plans(root)],
                             ["2026-09-14", "2026-09-07", "2026-08-31"])

    def test_counts_only_the_slots_cooked_at_home(self):
        self.assertEqual(plan_payload([self.plan])[0]["cooked"], 23)

    def test_a_day_nobody_cooked_is_not_flagged_against_the_goals(self):
        monday = plan_payload([self.plan])[0]["totals"]["monday"]
        self.assertEqual(monday["cooked"], 0)
        self.assertEqual(monday["flags"], [])

    def test_a_day_that_was_cooked_is_still_measured(self):
        sunday = plan_payload([self.plan])[0]["totals"]["sunday"]
        self.assertEqual(sunday["cooked"], 3)
        self.assertEqual(sunday["flags"], ["protein"])

    def test_a_plan_is_never_checked_against_a_layout(self):
        self.assertNotIn("violations", plan_payload([self.plan])[0])


class LastEaten(unittest.TestCase):
    """Variety is measured against weeks actually eaten, so each Recipe carries
    the last day a Plan put it on the table. Plan mode compares that with the
    reader's clock -- the page is committed, so "recent" cannot be baked in."""

    def plan(self, slug, days):
        return {"slug": slug, "title": "Week of " + slug, "days": days}

    def eaten(self, plans):
        return browse.last_eaten(plans)

    def test_dates_a_slot_from_the_plans_monday(self):
        dates = self.eaten([self.plan("2026-09-14", {"thursday": {"dinner": "steak"}})])
        self.assertEqual(dates["steak"], "2026-09-17")

    def test_a_plans_sunday_ends_its_week_rather_than_starting_it(self):
        dates = self.eaten([self.plan("2026-09-14", {"sunday": {"dinner": "steak"}})])
        self.assertEqual(dates["steak"], "2026-09-20")

    def test_the_latest_day_wins_across_plans(self):
        dates = self.eaten([
            self.plan("2026-09-14", {"monday": {"dinner": "steak"}}),
            self.plan("2026-09-07", {"saturday": {"dinner": "steak"}}),
            self.plan("2026-09-14", {"tuesday": {"lunch": "steak"}}),
        ])
        self.assertEqual(dates["steak"], "2026-09-15")

    def test_eaten_out_is_never_a_recipe(self):
        dates = self.eaten([self.plan("2026-09-14",
                                      {"monday": {s: browse.EATEN_OUT for s in browse.SLOTS}})])
        self.assertEqual(dates, {})

    def test_a_plan_not_named_for_a_date_is_ignored(self):
        dates = self.eaten([self.plan("draft", {"monday": {"dinner": "steak"}})])
        self.assertEqual(dates, {})

    def test_the_payload_carries_the_date_and_none_for_a_recipe_never_planned(self):
        rows = {r["slug"]: r for r in browse.build_payload({
            "recipes": RECIPES,
            "plans": [self.plan("2026-09-14", {"monday": {"dinner": "steak"}})],
            "pins": {}, "bands": {}, "goals": browse.DEFAULT_GOALS,
            "orders": [], "history": [],
        })["recipes"]}
        self.assertEqual(rows["steak"]["last_eaten"], "2026-09-14")
        self.assertIsNone(rows["bream"]["last_eaten"])


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

    def test_every_plan_fills_all_twenty_eight_slots(self):
        # bin/shopping-list.py treats a short grid as fatal, so a Slot nobody
        # cooked is spelled eaten-out rather than emptied.
        self.assertTrue(self.data["plans"], "Plans/ is empty")
        for plan in self.data["plans"]:
            filled = [s for slots in plan["days"].values() for s in slots.values() if s]
            self.assertEqual(len(filled), 28, plan["slug"])

    def test_every_plan_slot_is_a_recipe_or_eaten_out(self):
        self.assertTrue(self.data["plans"], "Plans/ is empty")
        unresolved = sorted({s for plan in self.data["plans"]
                             for slots in plan["days"].values() for s in slots.values()
                             if s != browse.EATEN_OUT and s not in self.data["recipes"]})
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

    def test_the_page_only_fetches_its_pinned_ui_library(self):
        """Ticket 24's amendment allows exactly one runtime fetch: the pinned
        Bootstrap build, by exact URL. Anything else external creeping in --
        an accidental second CDN dependency, a typo'd version -- is what
        this test exists to catch, same as the old absolute-zero version did
        before there was a reason to allow one."""
        bootstrap_css = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css"
        bootstrap_js = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"
        scripts = re.findall(r'<script src="([^"]+)"', self.html)
        links = re.findall(r'<link[^>]*rel="stylesheet"[^>]*>', self.html)
        self.assertEqual(scripts, [bootstrap_js])
        self.assertEqual(len(links), 1)
        self.assertIn(bootstrap_css, links[0])

    def test_the_page_carries_no_redacted_string(self):
        browse.assert_no_pii(self.html, self.data["raw_orders"])

    def test_the_page_inlines_every_recipe_title(self):
        for recipe in self.data["recipes"].values():
            self.assertIn(json.dumps(recipe["title"])[1:-1], self.html)

    def test_the_page_inlines_every_planned_week(self):
        for plan in self.data["plans"]:
            self.assertIn(plan["slug"], self.html)

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


BOOT = re.compile(r"\(function\(\)\{\s*var saved = null;.*?\}\)\(\);", re.S)

HARNESS = """
const results = {};
const bsResults = {};
for (const [saved, sysDark] of CASES) {
  globalThis.document = {documentElement: {dataset: {}}};
  globalThis.localStorage = {getItem() {
    if (saved === 'THROW') throw new Error('localStorage is denied here');
    return saved;
  }};
  globalThis.matchMedia = () => ({matches: sysDark});
  BOOT
  results[saved + '|' + sysDark] = document.documentElement.dataset.theme;
  bsResults[saved + '|' + sysDark] = document.documentElement.dataset.bsTheme;
}
console.log(JSON.stringify({theme: results, bsTheme: bsResults}));
"""

CASES = [
    ("dark", False), ("dark", True),
    ("light", False), ("light", True),
    (None, False), (None, True),
    ("THROW", True),
]


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class ThemeBootScript(unittest.TestCase):
    """The theme is decided before first paint by a script in <head>, and the
    branch it takes is the difference between a dark kitchen at 6am and a
    faceful of cream. Python cannot reach it, so node runs the real thing --
    lifted out of TEMPLATE, never retyped, so the test cannot drift from what
    ships.

    Two states, not three: a stored value IS the override, and its absence
    means follow the system.
    """

    @classmethod
    def setUpClass(cls):
        boot = BOOT.search(browse.TEMPLATE)
        assert boot, "the theme boot script is no longer in TEMPLATE"
        script = (HARNESS
                  .replace("CASES", json.dumps(CASES))
                  .replace("BOOT", boot.group(0)))
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as handle:
            handle.write(script)
            path = handle.name
        try:
            out = subprocess.run([shutil.which("node"), path], check=True,
                                 capture_output=True, text=True).stdout
        finally:
            os.unlink(path)
        data = json.loads(out)
        cls.themes = data["theme"]
        cls.bs_themes = data["bsTheme"]

    def test_a_stored_dark_beats_a_light_system(self):
        self.assertEqual(self.themes["dark|false"], "dark")

    def test_a_stored_dark_agrees_with_a_dark_system(self):
        self.assertEqual(self.themes["dark|true"], "dark")

    def test_a_stored_light_overrides_a_dark_system(self):
        self.assertEqual(self.themes["light|true"], "light")

    def test_a_stored_light_agrees_with_a_light_system(self):
        self.assertEqual(self.themes["light|false"], "light")

    def test_no_stored_choice_follows_a_dark_system(self):
        self.assertEqual(self.themes["null|true"], "dark")

    def test_no_stored_choice_follows_a_light_system(self):
        self.assertEqual(self.themes["null|false"], "light")

    def test_a_refusing_localstorage_still_renders_a_theme(self):
        """Privacy modes and some file:// origins throw. A theme preference
        must never be able to stop the page rendering."""
        self.assertEqual(self.themes["THROW|true"], "dark")

    def test_bs_theme_mirrors_theme(self):
        """Bootstrap's own color-mode CSS reads data-bs-theme, not data-theme
        -- the two must never disagree, in every one of the seven cases."""
        self.assertEqual(self.bs_themes, self.themes)


EATEN_AGO = re.compile(r"function eatenAgo\(iso, now\)\{.*?\n\}", re.S)

# Local noon, so no case sits on a midnight a timezone could tip over.
AGO_CASES = {
    "today": ["2026-09-24", [2026, 8, 24, 12]],
    "yesterday": ["2026-09-23", [2026, 8, 24, 12]],
    "fourteen": ["2026-09-10", [2026, 8, 24, 12]],
    "fifteen": ["2026-09-09", [2026, 8, 24, 12]],
    "tomorrow": ["2026-09-25", [2026, 8, 24, 12]],
    "never": [None, [2026, 8, 24, 12]],
    "across_bst_end": ["2026-10-20", [2026, 9, 27, 12]],
}


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class EatenAgo(unittest.TestCase):
    """Plan mode's badge: days since a Recipe was last eaten, within the two
    weeks variety is judged over, or nothing. Lifted out of TEMPLATE like the
    theme boot script, so the test runs what ships."""

    @classmethod
    def setUpClass(cls):
        fn = EATEN_AGO.search(browse.TEMPLATE)
        assert fn, "eatenAgo is no longer in TEMPLATE"
        script = fn.group(0) + """
const out = {};
for (const [k, [iso, d]] of Object.entries(%s)) out[k] = eatenAgo(iso, new Date(...d));
console.log(JSON.stringify(out));
""" % json.dumps(AGO_CASES)
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as handle:
            handle.write(script)
            path = handle.name
        try:
            # The household's clock, so the clock-change case has a clock change.
            env = dict(os.environ, TZ="Europe/London")
            out = subprocess.run([shutil.which("node"), path], check=True,
                                 capture_output=True, text=True, env=env).stdout
        finally:
            os.unlink(path)
        cls.ago = json.loads(out)

    def test_eaten_today_is_zero_days_ago(self):
        self.assertEqual(self.ago["today"], 0)

    def test_eaten_yesterday_is_one_day_ago(self):
        self.assertEqual(self.ago["yesterday"], 1)

    def test_fourteen_days_ago_is_still_recent(self):
        self.assertEqual(self.ago["fourteen"], 14)

    def test_fifteen_days_ago_is_not(self):
        self.assertIsNone(self.ago["fifteen"])

    def test_a_day_not_yet_reached_was_not_eaten(self):
        """A Plan already written for this week must not flag its own
        Recipes as eaten before the day comes."""
        self.assertIsNone(self.ago["tomorrow"])

    def test_a_recipe_never_planned_has_no_badge(self):
        self.assertIsNone(self.ago["never"])

    def test_counts_calendar_days_across_a_clock_change(self):
        """The clocks go back on 25 October; a 23- or 25-hour day is still
        one day."""
        self.assertEqual(self.ago["across_bst_end"], 7)


if __name__ == "__main__":
    unittest.main(verbosity=2)
