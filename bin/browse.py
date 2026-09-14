#!/usr/bin/env python3
"""Generate index.html -- the browse interface for this repo.

The second and last piece of code this project authorises, ruled in
.scratch/meal-planning-system/issues/24-browse-the-pool.md.

Reads Recipes/, Menus/, PINS.md, GOALS.md and Orders/, and writes one
self-contained index.html at the repo root with every datum inlined as JSON.
No server, no build step, no runtime fetches -- it opens over file:// and it
is served by GitHub Pages from the branch root.

Orders/ holds real personal data. Everything this file emits from them is
redacted, and assert_no_pii() refuses to write a page that carries a redacted
string. Run tests/test_browse.py after touching any of it.

Usage: bin/browse.py [--check]
"""

import glob
import json
import os
import re
import sys

import yaml

# Categories dropped from the published page in their entirety.
REDACTED_CATEGORIES = {"Toiletries, Health & Beauty"}

# Not an item category: the order's own footer.
COST_BREAKDOWN = "Cost breakdown"

ORDER_DATE = re.compile(r"^#\s+Waitrose Order\s+[-—]\s+(.+?)\s*$", re.M)
ORDER_PREAMBLE = re.compile(
    r"Order number\s+(\d+)\.\s+Collected\s+[^,]+,\s*([^,]+),\s*from\s+(.+?)\.\s*$",
    re.M,
)
ORDER_HEADING = re.compile(r"^###\s+(.+?)\s*$", re.M)
ORDER_ROW = re.compile(
    r"^\|\s*(\d{6})\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*$", re.M
)
ORDER_TOTAL = re.compile(r"^-\s+\*\*Total:\s*(.+?)\*\*\s*$", re.M)


class Failure(Exception):
    """A violation that makes the page wrong or unsafe. Stop; do not write it."""


def json_dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def parse_order(text, filename):
    """Parse one Orders/*.md into the redacted shape the page may show.

    The preamble line -- order number, collection window, branch, postcode --
    is never read into the result, and REDACTED_CATEGORIES never becomes a
    category. Redaction is by omission at parse time, so no later stage can
    reintroduce what was dropped.
    """
    date = ORDER_DATE.search(text)
    if not date:
        raise Failure(f"{filename} has no `# Waitrose Order -- <date>` heading")

    sections = []
    for heading in ORDER_HEADING.finditer(text):
        sections.append((heading.group(1), heading.end()))

    categories = []
    for index, (name, start) in enumerate(sections):
        end = sections[index + 1][1] if index + 1 < len(sections) else len(text)
        if name == COST_BREAKDOWN or name in REDACTED_CATEGORIES:
            continue
        items = [
            {
                "line": row.group(1),
                "item": row.group(2),
                "size": row.group(3),
                "qty": int(row.group(4)),
                "cost": row.group(5),
            }
            for row in ORDER_ROW.finditer(text[start:end])
        ]
        if items:
            categories.append({"name": name, "items": items})

    total = ORDER_TOTAL.search(text)
    return {
        "file": filename,
        "date": date.group(1),
        "categories": categories,
        "total": total.group(1) if total else None,
        "redacted": sorted(REDACTED_CATEGORIES),
    }


def pii_strings(text):
    """Every string from one raw order that must not reach the page."""
    forbidden = set()

    preamble = ORDER_PREAMBLE.search(text)
    if preamble:
        forbidden.add(preamble.group(1))          # order number
        window = preamble.group(2)                # 10:00am-11:00am
        forbidden.add(window)
        forbidden.update(part for part in re.split(r"[-—–]", window) if part.strip())
        for part in preamble.group(3).split(","):  # branch, postcode
            if part.strip():
                forbidden.add(part.strip())

    for name in REDACTED_CATEGORIES:
        match = re.search(
            r"^###\s+" + re.escape(name) + r"\s*$(.*?)(?=^###\s|\Z)", text, re.M | re.S
        )
        if match:
            for row in ORDER_ROW.finditer(match.group(1)):
                forbidden.add(row.group(1))
                forbidden.add(row.group(2))

    return {value.strip() for value in forbidden if value.strip()}


def assert_no_pii(html, raw_orders):
    """Refuse a page carrying anything the redaction was supposed to remove."""
    leaked = sorted(
        {value for text in raw_orders for value in pii_strings(text) if value in html}
    )
    if leaked:
        raise Failure(
            "redaction leaked into the page -- not written:\n  " + "\n  ".join(leaked)
        )


# Mirrors GOALS.md's Nutrient Goals. Duplicated deliberately so the pure
# functions stay testable without a file read; tests/test_browse.py asserts
# these equal what GOALS.md actually says, which turns the duplication into a
# checked invariant rather than drift waiting to happen.
DEFAULT_GOALS = {"protein_floor": 120.0, "kcal_ceiling": 1800.0}

DAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
SLOTS = ["breakfast", "lunch", "dinner", "pudding"]

# GOALS.md's Weekly Layout, as something a page can check a Menu against.
BREAKFAST_SPLIT = {"sausage": 3, "egg": 4}
LUNCH_TYPES = {"tofu", "chicken"}
LUNCH_FLOOR = 2
FIXED_DINNERS = {
    "sunday": "white-fish",
    "monday": "white-fish",
    "tuesday": "chicken",
    "wednesday": "oily-fish",
    "thursday": "beef",
}
FAKEAWAY_DAY = "friday"
FREE_DINNER_DAY = "saturday"

# A Plan Slot the household did not cook. VOCABULARY.md, The Plan grid.
EATEN_OUT = "eaten-out"

BAND_ROW = re.compile(
    r"^\|\s*(Breakfast|Lunch|Dinner|Pudding)\s*\|\s*~?([\d.]+)g?\s*\|\s*~?([\d.]+)\s*\|"
    r"\s*([\d.]+)\s*[-–—]\s*([\d.]+)g?\s*\|\s*([\d.]+)\s*[-–—]\s*([\d.]+)\s*\|",
    re.M,
)
PROTEIN_FLOOR = re.compile(r"\*\*Protein:\s*~?([\d.]+)g/day,\s*as a floor")
KCAL_CEILING = re.compile(r"\*\*Calories:\s*~?([\d.]+)/day,\s*as a ceiling")


def humanise(slug):
    return slug.replace("-", " ").capitalize()


def parse_bands(text):
    """The four Macro Bands from GOALS.md, keyed by Slot."""
    bands = {}
    for row in BAND_ROW.finditer(text):
        bands[row.group(1).lower()] = {
            "protein_target": float(row.group(2)),
            "kcal_target": float(row.group(3)),
            "protein_range": [float(row.group(4)), float(row.group(5))],
            "kcal_range": [float(row.group(6)), float(row.group(7))],
        }
    if not bands:
        raise Failure("GOALS.md has no Macro Bands table")
    return bands


def parse_nutrient_goals(text):
    """The daily protein floor and kcal ceiling from GOALS.md."""
    floor, ceiling = PROTEIN_FLOOR.search(text), KCAL_CEILING.search(text)
    if not floor or not ceiling:
        raise Failure("GOALS.md has no protein floor / kcal ceiling")
    return {"protein_floor": float(floor.group(1)),
            "kcal_ceiling": float(ceiling.group(1))}


def band_score(value, band, kind):
    """Where one macro sits against its Slot's range. Guidance, never a gate."""
    low, high = band[f"{kind}_range"]
    if value < low:
        return "under"
    if value > high:
        return "over"
    return "in"


def annotate_ingredient(line, pins):
    """A Recipe's ingredient line joined to its Pin, or flagged Unpinned."""
    key = line["ingredient"]
    pin = pins.get(key)
    out = {"ingredient": key}
    for field in ("qty", "unit", "note", "prep"):
        if field in line:
            out[field] = line[field]
    out.update({
        "display": (pin or {}).get("display") or humanise(key),
        "store": (pin or {}).get("store") if pin else None,
        "staple": bool((pin or {}).get("staple")),
        "product": (pin or {}).get("search_term") if pin else None,
        "line": (pin or {}).get("line_number") if pin else None,
        "pinned": pin is not None,
    })
    return out


def day_totals(slots, recipes):
    """Sum a day from its Recipes -- never from a Menu's hand-written table."""
    protein = kcal = 0.0
    for slug in slots.values():
        if slug == EATEN_OUT or slug not in recipes:
            continue
        macros = recipes[slug].get("macros") or {}
        protein += float(macros.get("protein_g") or 0)
        kcal += float(macros.get("kcal") or 0)
    return {"protein_g": round(protein, 1), "kcal": round(kcal, 1)}


def goal_flags(totals, goals=None):
    """Which of the two daily goals a day misses. Reported, never enforced."""
    goals = goals or DEFAULT_GOALS
    flags = []
    if totals["protein_g"] < goals["protein_floor"]:
        flags.append("protein")
    if totals["kcal"] > goals["kcal_ceiling"]:
        flags.append("kcal")
    return flags


def _protein_of(slug, recipes):
    return (recipes.get(slug) or {}).get("protein")


def layout_violations(days, recipes):
    """Where a Menu departs from GOALS.md's Weekly Layout."""
    out = []

    breakfasts = {}
    for day in DAYS:
        kind = _protein_of(days.get(day, {}).get("breakfast"), recipes)
        breakfasts[kind] = breakfasts.get(kind, 0) + 1
    for kind, want in BREAKFAST_SPLIT.items():
        got = breakfasts.get(kind, 0)
        if got != want:
            out.append(f"breakfast: {got}x {kind}, layout wants {want}x")
    stray = sorted(k for k in breakfasts if k not in BREAKFAST_SPLIT)
    if stray:
        out.append("breakfast: " + ", ".join(f"{k} is not a breakfast type" for k in stray))

    lunches = {}
    for day in DAYS:
        kind = _protein_of(days.get(day, {}).get("lunch"), recipes)
        lunches[kind] = lunches.get(kind, 0) + 1
    for kind in sorted(LUNCH_TYPES):
        if lunches.get(kind, 0) < LUNCH_FLOOR:
            out.append(f"lunch: {lunches.get(kind, 0)}x {kind}, layout wants at least {LUNCH_FLOOR}")
    for kind in sorted(k for k in lunches if k not in LUNCH_TYPES):
        out.append(f"lunch: {kind} is neither tofu nor chicken")

    for day, want in FIXED_DINNERS.items():
        got = _protein_of(days.get(day, {}).get("dinner"), recipes)
        if got != want:
            out.append(f"{day.capitalize()} dinner: {got or 'nothing'}, layout fixes {want}")
    friday = days.get(FAKEAWAY_DAY, {}).get("dinner")
    if "fakeaway" not in ((recipes.get(friday) or {}).get("tags") or []):
        out.append("Friday dinner: not tagged fakeaway")

    for day in DAYS:
        pudding = days.get(day, {}).get("pudding")
        if _protein_of(pudding, recipes):
            out.append(f"{day.capitalize()} pudding: carries a protein type")

    return out


def orphans(recipes, menus):
    """Recipes no Menu uses. The pool's own dead weight, made visible."""
    used = {slug for menu in menus for slots in menu["days"].values()
            for slug in slots.values()}
    return sorted(slug for slug in recipes if slug not in used)


def order_aggregate(orders, pins):
    """Every distinct line bought, how often, when, and whether it is Pinned."""
    by_line = {pin.get("line_number"): key for key, pin in pins.items()
               if pin.get("line_number")}
    rows = {}
    for order in orders:
        for category in order["categories"]:
            for item in category["items"]:
                row = rows.setdefault(item["line"], {
                    "line": item["line"], "item": item["item"],
                    "category": category["name"], "orders": 0, "qty": 0, "dates": [],
                    "pinned_as": by_line.get(item["line"]),
                })
                row["orders"] += 1
                row["qty"] += item["qty"]
                row["dates"].append(order["date"])
                row["item"] = item["item"]
    return sorted(rows.values(), key=lambda r: (-r["orders"], r["item"].lower()))


FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)
METHOD_STEP = re.compile(r"^\s*\d+\.\s+(.*?)\s*$", re.M)
HISTORY_ROW = re.compile(
    r"^\|\s*([^|]+?)\s*\|\s*(Completed|Cancelled)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|$",
    re.M,
)


def read(path):
    return open(path, encoding="utf-8").read()


def split_document(path):
    """Frontmatter as a dict, body as text. The shape every Recipe and Menu has."""
    match = FRONTMATTER.match(read(path))
    if not match:
        raise Failure(f"{path} has no frontmatter block")
    return yaml.safe_load(match.group(1)), match.group(2)


def load_pins(root):
    blocks = re.findall(r"```yaml\n(.*?)```", read(os.path.join(root, "PINS.md")), re.S)
    if not blocks:
        raise Failure("PINS.md contains no yaml catalogue block")
    return yaml.safe_load(blocks[0])


def load_recipes(root):
    recipes = {}
    for path in sorted(glob.glob(os.path.join(root, "Recipes", "*.md"))):
        front, body = split_document(path)
        slug = os.path.basename(path)[:-3]
        front["slug"] = slug
        front["method"] = METHOD_STEP.findall(body)
        recipes[slug] = front
    if not recipes:
        raise Failure("Recipes/ is empty")
    return recipes


def load_menus(root):
    menus = []
    for path in sorted(glob.glob(os.path.join(root, "Menus", "*.md"))):
        front, _ = split_document(path)
        menus.append({
            "slug": os.path.basename(path)[:-3],
            "title": front.get("title") or humanise(os.path.basename(path)[:-3]),
            "days": {day: dict(front.get("days", {}).get(day) or {}) for day in DAYS},
        })
    return menus


def load_orders(root):
    """Every captured order, parsed and redacted, oldest first."""
    parsed, raw = [], []
    for path in sorted(glob.glob(os.path.join(root, "Orders", "*.md"))):
        name = os.path.basename(path)
        if name in ("HARVEST.md", "BASKET.md", "history.md"):
            continue
        text = read(path)
        raw.append(text)
        parsed.append(parse_order(text, name))
    parsed.sort(key=lambda o: _order_key(o["date"]))
    return parsed, raw


MONTHS = ["january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"]


def _order_key(date):
    parts = date.replace(",", " ").split()
    day = month = year = 0
    for part in parts:
        if part.isdigit() and len(part) == 4:
            year = int(part)
        elif part.isdigit():
            day = int(part)
        elif part.lower() in MONTHS:
            month = MONTHS.index(part.lower()) + 1
    return (year, month, day)


def load_history(root):
    """Orders/history.md: the index of what exists, captured or not."""
    path = os.path.join(root, "Orders", "history.md")
    if not os.path.isfile(path):
        return []
    return [
        {"date": row.group(1), "status": row.group(2),
         "total": row.group(3), "captured": row.group(4)}
        for row in HISTORY_ROW.finditer(read(path))
    ]


def load_all(root):
    goals_text = read(os.path.join(root, "GOALS.md"))
    orders, raw_orders = load_orders(root)
    return {
        "recipes": load_recipes(root),
        "menus": load_menus(root),
        "pins": load_pins(root),
        "bands": parse_bands(goals_text),
        "goals": parse_nutrient_goals(goals_text),
        "orders": orders,
        "raw_orders": raw_orders,
        "history": load_history(root),
    }


def build_payload(data):
    """Everything the page shows, resolved once here so the browser only renders."""
    recipes, pins, bands = data["recipes"], data["pins"], data["bands"]
    menus, orders = data["menus"], data["orders"]

    # Which Menus use a Recipe, and where. The Menu is the cross-link's owner,
    # so it is walked once and the answer hung on the Recipe.
    used_by = {slug: [] for slug in recipes}
    for menu in menus:
        for day in DAYS:
            for slot in SLOTS:
                slug = menu["days"].get(day, {}).get(slot)
                if slug in used_by:
                    used_by[slug].append(
                        {"menu": menu["slug"], "title": menu["title"],
                         "day": day, "slot": slot})

    recipe_rows = []
    for slug in sorted(recipes):
        recipe = recipes[slug]
        slot = recipe.get("slot")
        band = bands.get(slot)
        macros = recipe.get("macros") or {}
        ingredients = [annotate_ingredient(line, pins)
                       for line in (recipe.get("ingredients") or [])]
        method = recipe.get("method") or []
        # Both vocabularies, deliberately. A Recipe says parmesan and pine
        # nuts; the shelf says Parmigiano Reggiano and Pine Kernels. Searching
        # only one of them misses whichever word the reader happens to know.
        haystack = " ".join(
            [recipe.get("title", ""), slug]
            + [i["display"] for i in ingredients]
            + [i["ingredient"] for i in ingredients]
            + [i["product"] for i in ingredients if i["product"]]
            + method
        ).lower()
        recipe_rows.append({
            "slug": slug,
            "title": recipe.get("title") or humanise(slug),
            "slot": slot,
            "protein": recipe.get("protein"),
            "effort": recipe.get("effort"),
            # Human-only, and absent on most Recipes. VOCABULARY.md: nothing
            # infers a rating, so an unrated Recipe carries None and sorts last.
            "rating": recipe.get("rating"),
            "appliances": recipe.get("appliances") or [],
            "tags": recipe.get("tags") or [],
            "protein_g": macros.get("protein_g"),
            "kcal": macros.get("kcal"),
            "band": band,
            "score": {
                "protein": band_score(macros.get("protein_g") or 0, band, "protein") if band else None,
                "kcal": band_score(macros.get("kcal") or 0, band, "kcal") if band else None,
            },
            "ingredients": ingredients,
            "unpinned": sorted({i["ingredient"] for i in ingredients if not i["pinned"]}),
            "method": method,
            "used_by": used_by[slug],
            "haystack": haystack,
        })

    menu_rows = []
    for menu in menus:
        totals = {}
        for day in DAYS:
            day_slots = menu["days"].get(day, {})
            summed = day_totals(day_slots, recipes)
            summed["flags"] = goal_flags(summed, data["goals"])
            totals[day] = summed
        composition = {}
        for slot in SLOTS:
            counts = {}
            for day in DAYS:
                slug = menu["days"].get(day, {}).get(slot)
                kind = (recipes.get(slug) or {}).get("protein") or "—"
                counts[kind] = counts.get(kind, 0) + 1
            composition[slot] = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        menu_rows.append({
            "slug": menu["slug"],
            "title": menu["title"],
            "days": menu["days"],
            "totals": totals,
            "week": {
                "protein_g": round(sum(t["protein_g"] for t in totals.values()), 1),
                "kcal": round(sum(t["kcal"] for t in totals.values()), 1),
            },
            "composition": composition,
            "violations": layout_violations(menu["days"], recipes),
        })

    aggregate = order_aggregate(orders, pins)
    bought = {row["line"]: row for row in aggregate}
    pin_rows = []
    for key in sorted(pins):
        pin = pins[key]
        line = pin.get("line_number")
        row = bought.get(line) if line else None
        pin_rows.append({
            "key": key,
            "display": pin.get("display") or humanise(key),
            "store": pin.get("store"),
            "line": line,
            "staple": bool(pin.get("staple")),
            "product": pin.get("search_term"),
            "orders": row["orders"] if row else 0,
            "last_bought": row["dates"][-1] if row else None,
        })

    facets = {field: sorted({v for r in recipe_rows for v in
                             (r[field] if isinstance(r[field], list) else [r[field]])
                             if v})
              for field in ("slot", "protein", "effort", "appliances", "tags")}

    return {
        "recipes": recipe_rows,
        "menus": menu_rows,
        "orders": orders,
        "aggregate": aggregate,
        "pins": pin_rows,
        "history": data["history"],
        "bands": bands,
        "goals": data["goals"],
        "facets": facets,
        "days": DAYS,
        "slots": SLOTS,
        "orphans": orphans(recipes, menus),
        "redacted": sorted(REDACTED_CATEGORIES),
    }


TEMPLATE = r"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meal Planning</title>
<style>
:root{
  --paper:#faf7f1; --card:#fffdf9; --ink:#332f29; --soft:#6f675c;
  --rule:#e4dccf; --accent:#95462a; --accent-soft:#f2e5dd;
  --under:#9a6a1f; --over:#8d3a3a; --in:#4d6b45;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);
  font-size:16px;line-height:1.5;-webkit-text-size-adjust:100%}
a{color:inherit;text-decoration:none}
h1,h2,h3{font-weight:600;letter-spacing:-.01em;margin:0}
.wrap{max-width:60rem;margin:0 auto;padding:0 1rem}

header{border-bottom:1px solid var(--rule);position:sticky;top:0;z-index:20;
  background:var(--paper)}
.brand{display:flex;align-items:baseline;gap:.6rem;padding:.9rem 0 .5rem}
.brand h1{font-size:1.15rem}
.brand span{font-size:.75rem;color:var(--soft);letter-spacing:.06em;text-transform:uppercase}
nav{display:flex;align-items:center;gap:1.25rem;padding-bottom:.1rem}
nav a{padding:.35rem 0 .55rem;font-size:.95rem;color:var(--soft);
  border-bottom:2px solid transparent}
nav a.on{color:var(--ink);border-bottom-color:var(--accent)}
/* Plan is a toggle, not a section -- a pill on the right, so it does not read
   as a fourth heading in a row of three. */
nav a#plantoggle{margin-left:auto;padding:.3rem .85rem;border:1px solid var(--rule);
  border-radius:999px;background:var(--card);font-size:.85rem;
  margin-bottom:.2rem;cursor:pointer}
nav a#plantoggle:hover{border-color:var(--accent);color:var(--accent)}
nav a#plantoggle.on{background:var(--accent);border-color:var(--accent);color:#fff}

main{padding:1.1rem 0 4rem}
.lede{color:var(--soft);font-size:.87rem;margin:.1rem 0 1rem}
.tools{display:flex;gap:.5rem;margin-bottom:1rem}
input[type=search]{flex:1;min-width:0;font:inherit;font-size:.95rem;color:inherit;
  background:var(--card);border:1px solid var(--rule);border-radius:2px;padding:.5rem .65rem}
input[type=search]:focus{outline:none;border-color:var(--accent)}
button,select{font:inherit;font-size:.9rem;color:inherit;background:var(--card);
  border:1px solid var(--rule);border-radius:2px;padding:.5rem .8rem;cursor:pointer}
button:hover,select:hover{border-color:var(--accent)}
select:focus{outline:none;border-color:var(--accent)}
.badge{display:inline-block;min-width:1.15rem;margin-left:.35rem;padding:0 .3rem;
  background:var(--accent);color:#fff;border-radius:999px;font-size:.72rem;text-align:center}

.sheet{position:fixed;inset:auto 0 0 0;z-index:30;background:var(--card);
  border-top:1px solid var(--rule);max-height:78vh;overflow:auto;padding:1rem;
  box-shadow:0 -8px 30px rgba(60,45,25,.12)}
.sheet[hidden]{display:none}
.scrim{position:fixed;inset:0;z-index:29;background:rgba(50,40,28,.25)}
.scrim[hidden]{display:none}
.facet{margin-bottom:1rem}
.facet h3{font-size:.72rem;letter-spacing:.09em;text-transform:uppercase;
  color:var(--soft);margin-bottom:.45rem}
.chips{display:flex;flex-wrap:wrap;gap:.35rem}
.chip{border:1px solid var(--rule);background:var(--paper);border-radius:999px;
  padding:.28rem .7rem;font-size:.85rem;cursor:pointer;color:var(--soft)}
.chip.on{background:var(--accent-soft);border-color:var(--accent);color:var(--accent)}
.slider{display:flex;align-items:center;gap:.7rem}
.slider input{flex:1}
.sheet-foot{display:flex;gap:.5rem;justify-content:space-between;
  border-top:1px solid var(--rule);padding-top:.75rem;margin-top:.5rem}

.group{margin:1.6rem 0 .5rem;display:flex;align-items:baseline;gap:.6rem;
  border-bottom:1px solid var(--rule);padding-bottom:.3rem}
.group h2{font-size:.78rem;letter-spacing:.1em;text-transform:uppercase;color:var(--accent)}
.group em{font-style:normal;font-size:.78rem;color:var(--soft)}
ul.list{list-style:none;margin:0;padding:0}
ul.list li{border-bottom:1px solid var(--rule)}
ul.list a{display:block;padding:.7rem .2rem}
ul.list a:hover{background:var(--card)}
.row{display:flex;gap:.75rem;align-items:baseline;justify-content:space-between}
.row .t{font-size:1rem}
.macro{white-space:nowrap;font-size:.85rem;color:var(--soft);font-variant-numeric:tabular-nums}
.meta{font-size:.78rem;color:var(--soft);margin-top:.15rem}
.dot{display:inline-block;width:.42rem;height:.42rem;border-radius:50%;
  vertical-align:.06rem;margin-right:.25rem}
.dot.in{background:var(--in)} .dot.under{background:var(--under)} .dot.over{background:var(--over)}
.empty{color:var(--soft);padding:2rem 0;text-align:center;font-style:italic}

.back{display:inline-block;font-size:.85rem;color:var(--soft);margin-bottom:.7rem}
.back:hover{color:var(--accent)}
article h2{font-size:1.35rem;line-height:1.25;margin-bottom:.35rem}
.tagline{font-size:.82rem;color:var(--soft);margin-bottom:1.1rem}
section{margin:1.6rem 0}
section > h3{font-size:.72rem;letter-spacing:.09em;text-transform:uppercase;
  color:var(--accent);border-bottom:1px solid var(--rule);padding-bottom:.25rem;
  margin-bottom:.7rem}
table{width:100%;border-collapse:collapse;font-size:.88rem}
th{text-align:left;font-weight:600;font-size:.72rem;letter-spacing:.06em;
  text-transform:uppercase;color:var(--soft);padding:.3rem .7rem;
  border-bottom:1px solid var(--rule)}
td{padding:.42rem .7rem;border-bottom:1px solid var(--rule);vertical-align:top}
th:first-child,td:first-child{padding-left:0}
th:last-child,td:last-child{padding-right:0}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.scroller{overflow-x:auto;-webkit-overflow-scrolling:touch}
ol.method{margin:0;padding-left:1.3rem}
ol.method li{margin-bottom:.6rem}
.note{font-size:.82rem;color:var(--soft)}
.warn{border-left:2px solid var(--accent);background:var(--accent-soft);
  padding:.6rem .8rem;font-size:.85rem;margin:.6rem 0}
.flag{color:var(--over);font-size:.78rem}
.pill{display:inline-block;border:1px solid var(--rule);border-radius:999px;
  padding:.05rem .55rem;font-size:.75rem;color:var(--soft);margin:0 .25rem .25rem 0}
.pill.un{border-color:var(--accent);color:var(--accent)}
.day{border-bottom:1px solid var(--rule);padding:.8rem 0}
.day h4{margin:0 0 .35rem;font-size:.82rem;letter-spacing:.08em;text-transform:uppercase;
  color:var(--soft);display:flex;justify-content:space-between;align-items:baseline}
.day dl{margin:0;display:grid;grid-template-columns:5.2rem 1fr;gap:.2rem .6rem}
.day dt{font-size:.75rem;color:var(--soft);text-transform:capitalize}
.day dd{margin:0;font-size:.92rem}
/* Plan mode. The drawer is its own thing, not a reused .sheet -- .sheet turns
   into a sticky sidebar on wide screens and this must stay at the bottom. */
.drawer{position:fixed;inset:auto 0 0 0;z-index:40;background:var(--card);
  border-top:1px solid var(--rule);box-shadow:0 -2px 14px rgba(50,40,28,.12);
  padding:.7rem 0}
.drawer .wrap{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap}
.drawer .where{font-size:.95rem}
.drawer .where b{text-transform:capitalize}
.drawer .rest{margin-left:auto;display:flex;gap:.5rem}
body.plan-on{padding-bottom:6rem}
body.plan-on .list a{cursor:pointer}
body.plan-on .list a:hover{background:var(--accent-soft)}
body.plan-on .list a:hover .t{color:var(--accent)}
button[disabled]{opacity:.45;cursor:not-allowed}
button[disabled]:hover{border-color:var(--rule)}
textarea{width:100%;font:inherit;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
  font-size:.82rem;line-height:1.5;color:inherit;background:var(--card);
  border:1px solid var(--rule);border-radius:2px;padding:.7rem}
.subnav{display:flex;gap:1rem;margin-bottom:1rem;font-size:.85rem}
.subnav a{color:var(--soft);border-bottom:1px solid transparent;padding-bottom:.15rem}
.subnav a.on{color:var(--accent);border-bottom-color:var(--accent)}

@media(min-width:56rem){
  body{font-size:17px}
  .layout{display:grid;grid-template-columns:14rem 1fr;gap:2rem;align-items:start}
  .sheet{position:sticky;top:6.2rem;inset:auto;max-height:none;overflow:visible;
    box-shadow:none;border:1px solid var(--rule);border-radius:2px;padding:.9rem}
  .sheet[hidden]{display:block}
  .scrim{display:none!important}
  .sheet-foot .close{display:none}
  #filterbtn{display:none}
  .day dl{grid-template-columns:6rem 1fr}
}
</style>

</head>
<body>
<header><div class="wrap">
  <div class="brand"><h1>Meal Planning</h1><span>plan the week, buy it once</span></div>
  <nav id="nav"></nav>
</div></header>
<main class="wrap"><div id="app"></div></main>
<div class="scrim" id="scrim" hidden></div>
<div class="drawer" id="drawer" hidden></div>

<script id="data" type="application/json">__PAYLOAD__</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const byslug = Object.fromEntries(D.recipes.map(r => [r.slug, r]));
const FACETS = ['slot','protein','effort','appliances','tags'];
/* Sort is per-group, not global: the Slot headings stay and the order inside
   each changes. An absent value sorts last in every mode -- unrated is
   unknown, not zero, and a blank rating must not read as a bad one. */
const SORTS = {
  title:   {label:'Title',   key: r => r.title.toLowerCase()},
  rating:  {label:'Rating',  key: r => r.rating,    desc:true},
  protein: {label:'Protein', key: r => r.protein_g, desc:true},
};

/* Absent last, then by key, then title as the tie-break so the order is
   total -- two 5s or two 47g Recipes must not shuffle between renders. */
function sorted(rs){
  const {key, desc} = SORTS[route.sort] || SORTS.title;
  return rs.slice().sort((x,y) => {
    const a = key(x), b = key(y);
    if (a == null || b == null) return a == null ? (b == null ? 0 : 1) : -1;
    if (a !== b) return (a < b ? -1 : 1) * (desc ? -1 : 1);
    return x.title.toLowerCase() < y.title.toLowerCase() ? -1 : 1;
  });
}
const star = n => n == null ? '' : '\u2605' + n;
const cap = s => s ? s.charAt(0).toUpperCase() + s.slice(1) : '';
const nice = s => s ? s.replace(/-/g,' ') : '';
const esc = s => String(s ?? '').replace(/[&<>"]/g, c =>
  ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
/* Every macro figure reaches the reader with a tilde. The numbers are
   estimates and CLAUDE.md makes the tilde the honest signal. */
const g = n => n == null ? '—' : '~' + (+n) + 'g';
const kc = n => n == null ? '—' : '~' + Math.round(n);

let route = {view:'recipes', slug:null, sub:null, f:{}, q:'', min:0, sort:'title'};

function readHash(){
  const raw = location.hash.replace(/^#/,'');
  const [path, query] = raw.split('?');
  const parts = (path || 'recipes').split('/');
  const r = {view: parts[0] || 'recipes', slug: parts[1] || null, sub: null,
             f:{}, q:'', min:0, sort:'title'};
  if (r.view === 'orders') { r.sub = parts[1] || 'orders'; r.slug = null; }
  const p = new URLSearchParams(query || '');
  r.q = p.get('q') || '';
  r.min = +(p.get('min') || 0);
  if (SORTS[p.get('sort')]) r.sort = p.get('sort');
  FACETS.forEach(k => { const v = p.get(k); if (v) r.f[k] = v.split(','); });
  return r;
}

function writeHash(r, replace){
  const p = new URLSearchParams();
  if (r.q) p.set('q', r.q);
  if (r.min) p.set('min', r.min);
  if (r.sort !== 'title') p.set('sort', r.sort);
  FACETS.forEach(k => { if ((r.f[k]||[]).length) p.set(k, r.f[k].join(',')); });
  let path = r.view;
  if (r.view === 'recipe' || r.view === 'menu') path += '/' + r.slug;
  if (r.view === 'orders' && r.sub && r.sub !== 'orders') path += '/' + r.sub;
  const s = p.toString();
  const hash = '#' + path + (s ? '?' + s : '');
  if (replace) history.replaceState(null,'',hash); else location.hash = hash;
}

/* Filters live in the hash so a filtered view is bookmarkable, survives a
   refresh, and is still there when Back returns from a Recipe. A Recipe link
   carries the query too, so the in-page "back" is as faithful as the browser's. */
function qs(){
  const p = new URLSearchParams();
  if (route.q) p.set('q', route.q);
  if (route.min) p.set('min', route.min);
  if (route.sort !== 'title') p.set('sort', route.sort);
  FACETS.forEach(k => { if ((route.f[k]||[]).length) p.set(k, route.f[k].join(',')); });
  const s = p.toString();
  return s ? '?' + s : '';
}
const listHash = () => '#recipes' + qs();

const activeCount = () =>
  FACETS.reduce((n,k) => n + (route.f[k]||[]).length, 0) + (route.min ? 1 : 0);

function matches(r){
  for (const k of FACETS){
    const want = route.f[k] || [];
    if (!want.length) continue;
    const have = Array.isArray(r[k]) ? r[k] : (r[k] ? [r[k]] : []);
    if (!want.some(v => have.includes(v))) return false;   /* OR within a facet */
  }
  if (route.min && (r.protein_g || 0) < route.min) return false;
  /* Substring, case-insensitive, no fuzzy matching. The haystack carries the
     Recipe's own words AND the Pinned product names, because those two
     vocabularies disagree -- parmesan / Parmigiano Reggiano. */
  if (route.q && !r.haystack.includes(route.q.toLowerCase())) return false;
  return true;
}

function scoreDot(kind, r){
  const s = r.score && r.score[kind];
  return s ? `<span class="dot ${s}" title="${kind} ${s} band"></span>` : '';
}

function renderNav(){
  const tabs = [['recipes','Recipes'],['menus','Menus'],['orders','Past orders'],
                ['plan','Plan']];
  const here = route.view === 'recipe' ? 'recipes'
             : route.view === 'menu' ? 'menus' : route.view;
  document.getElementById('nav').innerHTML = tabs.map(([v,label]) =>
    v === 'plan'
      ? `<a class="${planOn?'on':''}" href="#recipes" id="plantoggle"
           aria-pressed="${planOn}">${planOn ? 'Planning' : label}</a>`
      : `<a class="${v===here?'on':''}" href="#${v}">${label}</a>`).join('');
  /* Plan is a toggle, not a destination: it turns the pool into a picker and
     leaves you wherever the hash already was. */
  document.getElementById('plantoggle').onclick = event => {
    event.preventDefault();
    if (planOn) return planExit();
    planOn = true;
    if (route.view === 'recipes') render(); else location.hash = '#recipes';
  };
}

function facetPanel(){
  const rows = FACETS.map(k => `<div class="facet"><h3>${k}</h3><div class="chips">` +
    D.facets[k].map(v => {
      const on = (route.f[k]||[]).includes(v);
      return `<button class="chip ${on?'on':''}" data-facet="${k}" data-value="${v}">${nice(v)}</button>`;
    }).join('') + `</div></div>`).join('');
  return `<div class="sheet" id="sheet" hidden>
    ${rows}
    <div class="facet"><h3>Protein floor</h3><div class="slider">
      <input type="range" id="min" min="0" max="60" step="5" value="${route.min}">
      <span class="macro" id="minlabel">${route.min ? g(route.min)+'+' : 'any'}</span>
    </div></div>
    <div class="sheet-foot">
      <button id="clear">Clear all</button>
      <button class="close" id="done">Done</button>
    </div></div>`;
}

function recipeList(){
  /* While a Slot is being picked the pool narrows to Recipes of that Slot --
     the facets and the search box still apply on top. */
  const only = planOn && !checkedOut ? planSlot() : null;
  const hits = D.recipes.filter(r => (!only || r.slot === only) && matches(r));
  const groups = D.slots.map(slot => [slot, sorted(hits.filter(r => r.slot === slot))])
                        .filter(([,rs]) => rs.length);
  const body = groups.length ? groups.map(([slot, rs]) => `
    <div class="group"><h2>${slot}</h2><em>${rs.length}</em></div>
    <ul class="list">${rs.map(r => `<li><a href="#recipe/${r.slug}${qs()}">
      <div class="row"><span class="t">${esc(r.title)}</span>
        <span class="macro">${scoreDot('protein',r)}${g(r.protein_g)} · ${kc(r.kcal)} kcal</span></div>
      <div class="meta">${[star(r.rating), nice(r.protein), r.effort ? r.effort+' effort' : '',
        (r.appliances||[]).map(nice).join(', ') || 'no appliance',
        (r.tags||[]).map(nice).join(', ')].filter(Boolean).join(' · ')}</div>
    </a></li>`).join('')}</ul>`).join('')
    : `<p class="empty">No Recipe matches those filters.</p>`;

  const n = activeCount();
  return `<p class="lede">${D.recipes.length} Recipes${
      D.orphans.length ? ` · ${D.orphans.length} used by no Menu` : ''}.
      Showing ${hits.length}.</p>
    <div class="tools">
      <input type="search" id="q" placeholder="Search titles, ingredients, products, method"
             value="${esc(route.q)}">
      <select id="sort" aria-label="Sort within each Slot">${
        Object.entries(SORTS).map(([k,v]) =>
          `<option value="${k}"${k === route.sort ? ' selected' : ''}>${v.label}</option>`
        ).join('')}</select>
      <button id="filterbtn">Filters${n ? `<span class="badge">${n}</span>` : ''}</button>
    </div>
    <div class="layout">${facetPanel()}<div>${body}</div></div>`;
}

function recipeDetail(slug){
  const r = byslug[slug];
  if (!r) return `<p class="empty">No Recipe called ${esc(slug)}.</p>`;
  const b = r.band;
  const bandRow = (kind, value, unit) => {
    if (!b) return '';
    const s = r.score[kind];
    const target = kind === 'protein' ? g(b.protein_target) : kc(b.kcal_target);
    const lo = kind === 'protein' ? b.protein_range[0] : b.kcal_range[0];
    const hi = kind === 'protein' ? b.protein_range[1] : b.kcal_range[1];
    const fmt = kind === 'protein' ? g : kc;
    return `<tr><td>${cap(kind)}</td><td class="num">${fmt(value)}${unit}</td>
      <td class="num">${target}</td>
      <td class="num note">${fmt(lo)}–${fmt(hi)}</td>
      <td><span class="dot ${s}"></span>${s}</td></tr>`;
  };
  const ing = r.ingredients.map(i => `<tr>
    <td>${esc(i.display)}${i.note||i.prep ? `<div class="note">${esc(i.note||i.prep)}</div>`:''}</td>
    <td class="num">${i.qty != null ? esc(i.qty) + ' ' + esc(i.unit||'') : '—'}</td>
    <td>${i.pinned ? esc(i.store === 'dorset-meats' ? 'Dorset Meats'
          : i.store === 'soutars' ? 'Soutars' : cap(i.store||''))
          + (i.staple ? ' <span class="note">staple</span>' : '')
        : '<span class="pill un">unpinned</span>'}</td>
    <td class="note">${i.pinned ? esc(i.product || '—') : 'add by hand'}</td>
  </tr>`).join('');

  return `<a class="back" href="${listHash()}">← Recipes</a>
  <article>
    <h2>${esc(r.title)}</h2>
    <p class="tagline">${[star(r.rating), cap(r.slot), nice(r.protein), r.effort ? r.effort+' effort':'' ,
        (r.appliances||[]).map(nice).join(' · ')].filter(Boolean).join(' · ')}
      ${(r.tags||[]).map(t=>`<span class="pill">${nice(t)}</span>`).join('')}</p>

    <section><h3>Macros against the ${esc(r.slot)} Band</h3>
      <table><thead><tr><th>Macro</th><th class="num">This</th><th class="num">Target</th>
        <th class="num">Corpus range</th><th>Band</th></tr></thead>
        <tbody>${bandRow('protein', r.protein_g, '')}${bandRow('kcal', r.kcal, '')}</tbody></table>
      <p class="note">Serves 2. Bands guide, they do not gate — the goals are checked
        by summing a day, not by policing a Recipe.</p></section>

    <section><h3>Ingredients — ${r.ingredients.length}</h3>
      ${r.unpinned.length ? `<div class="warn"><strong>${r.unpinned.length} Unpinned:</strong>
        ${r.unpinned.map(nice).join(', ')}. No Pin exists, so the shopping list flags
        these to add by hand — and buying one puts it in the order history where
        the next harvest Pins it.</div>` : ''}
      <div class="scroller"><table><thead><tr><th>Ingredient</th><th class="num">Qty</th>
        <th>Store</th><th>Pinned product</th></tr></thead><tbody>${ing}</tbody></table></div>
    </section>

    <section><h3>Method</h3>
      <ol class="method">${r.method.map(s=>`<li>${esc(s)}</li>`).join('')}</ol></section>

    <section><h3>Used by</h3>
      ${r.used_by.length ? `<ul class="list">${r.used_by.map(u=>`<li><a href="#menu/${u.menu}">
        <div class="row"><span class="t">${esc(u.title)}</span>
        <span class="macro">${cap(u.day)} ${u.slot}</span></div></a></li>`).join('')}</ul>`
      : `<div class="warn">No Menu uses this Recipe. It is in the pool and in no
          rotation — an orphan.</div>`}</section>
  </article>`;
}

function menuList(){
  return `<p class="lede">${D.menus.length} Menus. Every one is 28 Slots — a Menu is
    never partial; a real week's deviation belongs to a Plan.</p>
    <ul class="list">${D.menus.map(m=>`<li><a href="#menu/${m.slug}">
      <div class="row"><span class="t">${esc(m.title)}</span>
      <span class="macro">${g((m.week.protein_g/7).toFixed(1))} · ${kc(m.week.kcal/7)} kcal / day</span></div>
      <div class="meta">${m.violations.length
        ? `<span class="flag">${m.violations.length} layout violation${m.violations.length>1?'s':''}</span>`
        : 'clears the Weekly Layout'} · ${
        Object.values(m.totals).filter(t=>t.flags.length).length} day(s) missing a goal</div>
    </a></li>`).join('')}</ul>`;
}

function menuDetail(slug){
  const m = D.menus.find(x => x.slug === slug);
  if (!m) return `<p class="empty">No Menu called ${esc(slug)}.</p>`;
  const days = D.days.map(day => {
    const t = m.totals[day];
    const cells = D.slots.map(s => {
      const r = byslug[m.days[day][s]];
      return `<dt>${s}</dt><dd>${r ? `<a href="#recipe/${r.slug}">${esc(r.title)}</a>
        <span class="note">${g(r.protein_g)}</span>` : '<span class="note">—</span>'}</dd>`;
    }).join('');
    return `<div class="day"><h4><span>${cap(day)}</span>
      <span class="macro">${g(t.protein_g)} · ${kc(t.kcal)} kcal
      ${t.flags.length ? `<span class="flag">↓${t.flags.join(' ')}</span>` : ''}</span></h4>
      <dl>${cells}</dl></div>`;
  }).join('');

  const comp = D.slots.map(s => `<tr><td>${cap(s)}</td><td>${
    m.composition[s].map(([k,n]) => `<span class="pill">${n}× ${nice(k)}</span>`).join('')
  }</td></tr>`).join('');

  return `<a class="back" href="#menus">← Menus</a>
  <article><h2>${esc(m.title)}</h2>
    <p class="tagline">28 Slots · ${g((m.week.protein_g/7).toFixed(1))} and
      ${kc(m.week.kcal/7)} kcal a day on average</p>

    <section><h3>Weekly Layout</h3>
      ${m.violations.length
        ? `<div class="warn"><strong>This Menu departs from GOALS.md:</strong><ul>${
            m.violations.map(v=>`<li>${esc(v)}</li>`).join('')}</ul></div>`
        : `<p class="note">Clean: 3 sausage / 4 egg breakfasts, at least 2 tofu and
            2 chicken lunches, the six fixed dinners in place and Saturday free.</p>`}
      <table><tbody>${comp}</tbody></table>
      <p class="note">Composition is computed from the Recipes, not read from any
        written table.</p></section>

    <section><h3>The week</h3>
      <p class="note">Day totals are summed from the Recipes each Slot names. If they
        disagree with the table written into <code>${esc(m.slug)}.md</code>, that drift
        is a bug worth seeing. Floor ${g(D.goals.protein_floor)}/day,
        ceiling ${kc(D.goals.kcal_ceiling)} kcal/day.</p>
      ${days}</section>
  </article>`;
}

/* Plan mode. The pool stays on screen and the wizard walks: the drawer names
   one Slot, a click on a Recipe fills it and advances. Selections live here for
   the session only -- the page is generated, not an app, and a refresh starting
   clean is honest where a stale grid would not be. */
const PLAN_SEQ = D.days.slice(1).concat(D.days.slice(0, 1))
  .flatMap(day => D.slots.map(slot => [day, slot]));
let plan = {};
let planOn = false;
let cursor = 0;
let checkedOut = false;

const planKey = ([day, slot]) => day + '.' + slot;
const planSlot = () => (PLAN_SEQ[cursor] || [])[1];
const planDone = () => PLAN_SEQ.filter(pair => plan[planKey(pair)]).length;

/* The Plan grid's own frontmatter shape -- two-space YAML, every Slot valued,
   a skipped Slot spelled `eaten-out`. VOCABULARY.md, The Plan grid. */
function planYaml(){
  const days = [...new Set(PLAN_SEQ.map(([day]) => day))];
  return 'days:\n' + days.map(day => '  ' + day + ':\n' +
    D.slots.map(s => '    ' + s + ': ' + plan[day + '.' + s]).join('\n')
  ).join('\n') + '\n';
}

function planSet(value){
  if (cursor >= PLAN_SEQ.length) return;
  plan[planKey(PLAN_SEQ[cursor])] = value;
  cursor++;
  render();
}

function planExit(){
  planOn = false; checkedOut = false; render();
}

function checkoutView(){
  return `<p class="lede">28 Slots, Monday first. A skipped Slot reads
      <code>eaten-out</code> — the grid's one reserved value, and the only thing
      besides a Recipe slug the shopping list accepts. It buys nothing. Paste this
      into <code>plan-the-week</code> at step 3, in place of the copied Menu grid.</p>
    <div class="tools"><button id="edit">← Back to the week</button>
      <button id="startover">Start over</button></div>
    <textarea id="out" rows="32" readonly>${esc(planYaml())}</textarea>`;
}

function renderDrawer(){
  const drawer = document.getElementById('drawer');
  document.body.classList.toggle('plan-on', planOn && !checkedOut);
  drawer.hidden = !planOn || checkedOut;
  if (drawer.hidden) return;

  const done = planDone();
  const at = PLAN_SEQ[cursor];
  const here = at
    ? `Pick <b>${cap(at[0])} ${at[1]}</b>${
        plan[planKey(at)] ? ` <span class="note">— holds ${
          plan[planKey(at)] === 'eaten-out' ? 'skipped'
          : esc((byslug[plan[planKey(at)]] || {}).title || '')}</span>` : ''}`
    : `<b>All 28 Slots filled.</b>`;

  drawer.innerHTML = `<div class="wrap">
    <span class="where">${here}</span>
    <span class="macro">${done} / ${PLAN_SEQ.length}</span>
    <span class="rest">
      <button id="planback"${cursor ? '' : ' disabled'}>← Back</button>
      ${at ? `<button id="planskip">Skip</button>` : ''}
      <button id="planout"${done < PLAN_SEQ.length ? ' disabled' : ''}>Checkout</button>
      <button id="planexit">Exit</button>
    </span></div>`;

  document.getElementById('planback').onclick = () => { cursor--; render(); };
  if (at) document.getElementById('planskip').onclick = () => planSet('eaten-out');
  document.getElementById('planout').onclick = () => { checkedOut = true; render(); };
  document.getElementById('planexit').onclick = planExit;
}

/* In plan mode a click on a Recipe fills the current Slot instead of opening
   the Recipe. Delegated, so it survives every re-render of the list. */
function wirePlanClicks(){
  document.getElementById('app').onclick = event => {
    if (!planOn || checkedOut) return;
    const link = event.target.closest('a[href^="#recipe/"]');
    if (!link) return;
    event.preventDefault();
    planSet(decodeURIComponent(link.getAttribute('href').split('?')[0].slice(8)));
  };
}

function wireCheckout(){
  const out = document.getElementById('out');
  out.focus(); out.select();
  document.getElementById('edit').onclick = () => { checkedOut = false; render(); };
  document.getElementById('startover').onclick = () => {
    plan = {}; cursor = 0; checkedOut = false; render(); };
}

function ordersView(){
  const sub = route.sub || 'orders';
  const tabs = [['orders','By order'],['items','Every item'],['pins','Pins']];
  const head = `<div class="subnav">${tabs.map(([v,l])=>
    `<a class="${v===sub?'on':''}" href="#orders${v==='orders'?'':'/'+v}">${l}</a>`).join('')}</div>`;

  if (sub === 'items'){
    const rows = D.aggregate.map(r=>`<tr>
      <td>${esc(r.item)}<div class="note">${esc(r.category)} · ${r.dates.map(esc).join(', ')}</div></td>
      <td class="num">${r.orders}</td><td class="num">${r.qty}</td>
      <td>${r.pinned_as ? `<span class="note">${nice(r.pinned_as)}</span>`
            : '<span class="pill un">not pinned</span>'}</td></tr>`).join('');
    const todo = D.aggregate.filter(r=>!r.pinned_as && r.orders>1).length;
    return head + `<p class="lede">${D.aggregate.length} distinct items across
      ${D.orders.length} orders. ${D.aggregate.filter(r=>!r.pinned_as).length} are not
      Pinned${todo ? `, and ${todo} of those were bought more than once — that is the
      pinning worklist` : ''}.</p>
      <div class="scroller"><table><thead><tr><th>Item</th><th class="num">Orders</th>
        <th class="num">Qty</th><th>Pin</th></tr></thead><tbody>${rows}</tbody></table></div>`;
  }

  if (sub === 'pins'){
    const rows = D.pins.map(p=>`<tr>
      <td>${esc(p.display)}<div class="note">${esc(p.key)}${p.staple?' · staple':''}</div></td>
      <td>${esc(p.store==='dorset-meats'?'Dorset Meats':p.store==='soutars'?'Soutars':cap(p.store||'—'))}</td>
      <td class="num">${p.line ? esc(p.line) : '—'}</td>
      <td>${p.orders ? `${p.orders}× <div class="note">last ${esc(p.last_bought)}</div>`
            : '<span class="note">not in a captured order</span>'}</td></tr>`).join('');
    return head + `<p class="lede">${D.pins.length} Pins, joined back to the orders by
      line number. A Pin with no order behind it is a hand-written decision — the
      counter proteins and the store-cupboard Staples are vetted that way.</p>
      <div class="scroller"><table><thead><tr><th>Pin</th><th>Store</th>
        <th class="num">Line</th><th>Bought</th></tr></thead><tbody>${rows}</tbody></table></div>`;
  }

  const cards = D.orders.slice().reverse().map(o => `
    <section><h3>${esc(o.date)} — ${esc(o.total||'')}</h3>
      ${o.categories.map(c=>`<h4 class="note" style="margin:.9rem 0 .2rem">${esc(c.name)}</h4>
        <div class="scroller"><table><thead><tr><th>Item</th><th>Size</th>
          <th class="num">Qty</th><th class="num">Cost</th></tr></thead>
          <tbody>${c.items.map(i=>`<tr><td>${esc(i.item)}
            <div class="note">${esc(i.line)}</div></td><td>${esc(i.size)}</td>
            <td class="num">${i.qty}</td><td class="num">${esc(i.cost)}</td></tr>`).join('')}
          </tbody></table></div>`).join('')}
    </section>`).join('');

  const hist = D.history.map(h=>`<tr><td>${esc(h.date)}</td><td>${esc(h.status)}</td>
    <td class="num">${esc(h.total)}</td><td class="note">${esc(h.captured)}</td></tr>`).join('');

  return head + `<p class="lede">${D.orders.length} captured orders.</p>
    <div class="warn">Order numbers, the collection branch, postcode and time window,
      and the ${D.redacted.join(' and ')} category are omitted from this page.
      They are in the repository's order files, not here.</div>
    ${cards}
    <section><h3>Order history</h3>
      <div class="scroller"><table><thead><tr><th>Date</th><th>Status</th>
        <th class="num">Total</th><th>Captured</th></tr></thead><tbody>${hist}</tbody></table></div>
    </section>`;
}

function render(){
  renderNav();
  const app = document.getElementById('app');
  const v = route.view;
  app.innerHTML =
      checkedOut    ? checkoutView()
    : v === 'recipe' ? recipeDetail(route.slug)
    : v === 'menus'  ? menuList()
    : v === 'menu'   ? menuDetail(route.slug)
    : v === 'orders' ? ordersView()
    : recipeList();
  renderDrawer();
  if (checkedOut) wireCheckout();
  else if (v === 'recipes' || v === undefined) { wireFilters(); wirePlanClicks(); }
  window.scrollTo(0, 0);
}

function wireFilters(){
  const sheet = document.getElementById('sheet');
  const scrim = document.getElementById('scrim');
  const wide = () => matchMedia('(min-width:56rem)').matches;
  const open = on => { sheet.hidden = !on; scrim.hidden = !on || wide(); };

  document.getElementById('filterbtn').onclick = () => open(sheet.hidden);
  document.getElementById('done').onclick = () => open(false);
  scrim.onclick = () => open(false);

  const q = document.getElementById('q');
  let timer;
  q.oninput = () => { clearTimeout(timer); timer = setTimeout(() => {
    route.q = q.value; writeHash(route, true);
    const at = q.selectionStart; render();
    const nq = document.getElementById('q'); nq.focus(); nq.setSelectionRange(at, at);
  }, 180); };

  const sort = document.getElementById('sort');
  sort.onchange = () => { route.sort = sort.value; writeHash(route, true); render(); };

  sheet.querySelectorAll('.chip').forEach(chip => chip.onclick = () => {
    const {facet, value} = chip.dataset;
    const cur = new Set(route.f[facet] || []);
    cur.has(value) ? cur.delete(value) : cur.add(value);
    route.f[facet] = [...cur];
    if (!route.f[facet].length) delete route.f[facet];
    writeHash(route, true); const wasOpen = !sheet.hidden;
    render(); if (wasOpen && !wide()) { document.getElementById('sheet').hidden = false;
      document.getElementById('scrim').hidden = false; }
  });

  const min = document.getElementById('min');
  min.oninput = () => { document.getElementById('minlabel').textContent =
    +min.value ? '~' + min.value + 'g+' : 'any'; };
  min.onchange = () => { route.min = +min.value; writeHash(route, true);
    const wasOpen = !sheet.hidden; render();
    if (wasOpen && !wide()) { document.getElementById('sheet').hidden = false;
      document.getElementById('scrim').hidden = false; } };

  document.getElementById('clear').onclick = () => {
    route.f = {}; route.q = ''; route.min = 0; writeHash(route, true); render(); };
}

addEventListener('hashchange', () => { route = readHash(); render(); });
route = readHash();
render();
</script>
</body>
</html>
"""


def render(data):
    payload = json_dump(build_payload(data))
    # `<` is escaped so no value can close the script element, and so the JSON
    # can never be mistaken for markup.
    payload = payload.replace("<", "\\u003c")
    return TEMPLATE.replace("__PAYLOAD__", payload)


def main(argv):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data = load_all(root)
    html = render(data)
    assert_no_pii(html, data["raw_orders"])

    out = os.path.join(root, "index.html")
    if "--check" in argv:
        current = read(out) if os.path.isfile(out) else None
        if current != html:
            raise Failure("index.html is stale -- re-run bin/browse.py")
        print("index.html is up to date")
        return 0

    with open(out, "w", encoding="utf-8") as handle:
        handle.write(html)
    payload = build_payload(data)
    print(
        f"index.html written: {len(payload['recipes'])} Recipes, "
        f"{len(payload['menus'])} Menus, {len(payload['orders'])} orders, "
        f"{len(payload['aggregate'])} distinct items, {len(html)} bytes."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Failure as exc:
        print(f"browse: {exc}", file=sys.stderr)
        sys.exit(1)
