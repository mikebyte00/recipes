#!/usr/bin/env python3
"""Generate index.html -- the browse interface for this repo.

The second and last piece of code this project authorises, ruled in
.scratch/meal-planning-system/issues/24-browse-the-pool.md.

Reads Recipes/, Plans/, PINS.md, GOALS.md and Orders/, and writes one
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
    """Sum a day from its Recipes -- never from a grid's hand-written table."""
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
    """Frontmatter as a dict, body as text. The shape every Recipe and Plan has."""
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


def load_plans(root):
    """Every week actually planned, latest first.

    A Plan is never checked against a layout: a real week deviates on purpose --
    days away, Slots eaten out, a Recipe swapped.
    """
    plans = []
    for path in sorted(glob.glob(os.path.join(root, "Plans", "*.md")), reverse=True):
        front, _ = split_document(path)
        slug = os.path.basename(path)[:-3]
        plans.append({
            "slug": slug,
            "title": front.get("title") or humanise(slug),
            "days": {day: dict(front.get("days", {}).get(day) or {}) for day in DAYS},
        })
    return plans


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
        "plans": load_plans(root),
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
    orders = data["orders"]

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
            "haystack": haystack,
        })

    plan_rows = []
    for plan in data["plans"]:
        totals, cooked = {}, 0
        for day in DAYS:
            slots = plan["days"].get(day, {})
            at_home = sum(1 for slot in SLOTS
                          if slots.get(slot) not in (None, EATEN_OUT))
            cooked += at_home
            summed = day_totals(slots, recipes)
            # A day nobody cooked misses both goals trivially. Flagging it would
            # report a night out as a nutritional failure.
            summed["flags"] = goal_flags(summed, data["goals"]) if at_home else []
            summed["cooked"] = at_home
            totals[day] = summed
        plan_rows.append({
            "slug": plan["slug"],
            "title": plan["title"],
            "days": plan["days"],
            "totals": totals,
            "cooked": cooked,
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
        "plans": plan_rows,
        "orders": orders,
        "aggregate": aggregate,
        "pins": pin_rows,
        "history": data["history"],
        "bands": bands,
        "goals": data["goals"],
        "facets": facets,
        "days": DAYS,
        "slots": SLOTS,
        "redacted": sorted(REDACTED_CATEGORIES),
    }


TEMPLATE = r"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meal Planning</title>
<!-- Pinned to an exact patch release with Subresource Integrity: a compromised
     CDN response is rejected by the browser rather than executed. Ticket 24's
     amendment accepts this as the page's one runtime fetch -- everything else
     it needs is still the inlined JSON payload below. -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css"
      rel="stylesheet"
      integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB"
      crossorigin="anonymous">
<!-- Before first paint, or the page flashes cream on the way to dark. The
     stored value IS the override; its absence means follow the system.
     localStorage throws in some privacy modes and on some file:// origins,
     and the page must still render -- hence the catch. -->
<script>
(function(){
  var saved = null;
  try { saved = localStorage.getItem('theme'); } catch (e) {}
  var dark = saved ? saved === 'dark'
                   : matchMedia('(prefers-color-scheme: dark)').matches;
  var theme = dark ? 'dark' : 'light';
  document.documentElement.dataset.theme = theme;
  document.documentElement.dataset.bsTheme = theme;
})();
</script>
<style>
/* Two themes, thirteen variables. `data-theme` is always set on <html> by the
   boot script in <head>, so the cascade never has to ask the media query --
   one light block, one dark block, and nothing duplicated between them. */
:root{
  color-scheme:light;
  --paper:#faf7f1; --card:#fffdf9; --ink:#332f29; --soft:#6f675c;
  --rule:#e4dccf; --accent:#95462a; --accent-soft:#f2e5dd;
  --under:#9a6a1f; --over:#8d3a3a; --in:#4d6b45;
  --on-accent:#fff; --shade:rgba(60,45,25,.12); --scrim:rgba(50,40,28,.25);
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --radius:12px;
  /* Bootstrap components read these, not the page's own --paper/--ink/etc,
     so every --bs-* variable a component actually formulas from (navbar
     colors, list-group hover/active, offcanvas chrome, form focus rings)
     is repointed here rather than overriding each component's own variable
     one by one. */
  --bs-body-bg: var(--paper); --bs-body-bg-rgb: 250,247,241;
  --bs-body-color: var(--ink); --bs-body-color-rgb: 51,47,41;
  --bs-emphasis-color: var(--ink); --bs-emphasis-color-rgb: 51,47,41;
  --bs-secondary-color: var(--soft); --bs-secondary-color-rgb: 111,103,92;
  --bs-tertiary-bg: var(--card); --bs-tertiary-bg-rgb: 255,253,249;
  --bs-border-color: var(--rule);
  --bs-border-color-translucent: var(--rule);
  --bs-primary: var(--accent); --bs-primary-rgb: 149,70,42;
}
/* Warm near-black, not a cold grey: the light theme is cream paper and burnt
   sienna, and a neutral dark would read as a different site. The accent
   lightens because #95462a on a dark ground fails contrast; --on-accent goes
   the other way for the same reason -- white text on the lightened accent
   would sit near 2:1. */
:root[data-theme=dark]{
  color-scheme:dark;
  --paper:#1a1714; --card:#221e19; --ink:#ece5da; --soft:#a49a8b;
  --rule:#3a332b; --accent:#e09468; --accent-soft:#3a2a20;
  --under:#d2a049; --over:#dd8585; --in:#8fbf7f;
  --on-accent:#1a1714; --shade:rgba(0,0,0,.5); --scrim:rgba(0,0,0,.55);
  --bs-body-bg: var(--paper); --bs-body-bg-rgb: 26,23,20;
  --bs-body-color: var(--ink); --bs-body-color-rgb: 236,229,218;
  --bs-emphasis-color: var(--ink); --bs-emphasis-color-rgb: 236,229,218;
  --bs-secondary-color: var(--soft); --bs-secondary-color-rgb: 164,154,139;
  --bs-tertiary-bg: var(--card); --bs-tertiary-bg-rgb: 34,30,25;
  --bs-border-color: var(--rule);
  --bs-border-color-translucent: var(--rule);
  --bs-primary: var(--accent); --bs-primary-rgb: 224,148,104;
}
*{box-sizing:border-box}
/* Two roles: serif carries the identity -- the wordmark and a Recipe/Plan's
   own title, the closest thing this page has to a dish on a plate. Everything
   you use to navigate, scan or filter is sans -- a serif at 13px is where
   "distinctive" turns into "scratchy". */
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  font-size:16px;line-height:1.6;-webkit-text-size-adjust:100%;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
a{color:inherit;text-decoration:none}
h1,h2,h3{font-weight:600;margin:0}
.wrap{max-width:64rem;margin:0 auto;padding:0 clamp(1rem,4vw,2rem)}

.brand{display:flex;align-items:center;gap:.7rem;padding:1.15rem 0 .7rem}
.brand h1{font-family:var(--serif);font-size:1.3rem;letter-spacing:-.01em}
.brand span{font-size:.85rem;color:var(--soft)}
/* Four tabs plus the pill overflow 360px. Scroll rather than wrap -- a wrapped
   nav pushes the list down the fold on the smallest phone. */
#nav{gap:1.5rem;padding-bottom:.2rem;overflow-x:auto;scrollbar-width:none}
#nav::-webkit-scrollbar{display:none}
#nav a{padding:.65rem 0 .75rem;font-size:1rem;color:var(--soft);
  white-space:nowrap;border-bottom:2px solid transparent;transition:color .15s,border-color .15s}
#nav a.on{color:var(--ink);border-bottom-color:var(--accent)}
/* Plan is a toggle, not a section -- a pill on the right, so it does not read
   as a fourth heading in a row of three. */
#nav a#plantoggle{margin-left:auto;padding:.45rem 1.1rem;border:1px solid var(--rule);
  border-radius:999px;background:var(--card);font-size:.9rem;
  margin-bottom:.3rem;cursor:pointer}
#nav a#plantoggle:hover{border-color:var(--accent);color:var(--accent)}
#nav a#plantoggle.on{background:var(--accent);border-color:var(--accent);color:var(--on-accent)}

main{padding:clamp(1.4rem,2vw,2.2rem) 0 5rem}
.lede{color:var(--soft);font-size:.95rem;line-height:1.6;margin:.1rem 0 1.5rem}
.tools{display:flex;gap:.6rem;margin-bottom:1.5rem;flex-wrap:wrap}
/* Quick Slot filtering below the search bar so it survives the sheet
   collapsing behind Filters on narrow screens. The sheet keeps its own Slot
   group too -- .facet[data-facet=slot] and .quickbar swap visibility at the
   same breakpoint the sheet itself collapses at, so wide screens are
   unchanged and narrow ones see Slot exactly once. */
.quickbar{display:flex;flex-wrap:wrap;gap:.45rem;margin:-.9rem 0 1.5rem}
input[type=search]{flex:1;min-width:10rem;font:inherit;font-size:1rem;color:inherit;
  background:var(--card);border:1px solid var(--rule);border-radius:9px;padding:.7rem .9rem;
  transition:border-color .15s}
button,select{font:inherit;font-size:.95rem;color:inherit;background:var(--card);
  border:1px solid var(--rule);border-radius:9px;padding:.65rem 1rem;cursor:pointer;
  transition:border-color .15s,color .15s}
button:hover,select:hover{border-color:var(--accent);color:var(--accent)}
/* The old rules removed the outline and left a border-colour change as the only
   focus signal, which a keyboard user cannot see on a control that has no
   border to begin with. :focus-visible keeps the mouse clean and gives the
   keyboard a ring. */
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--accent)}
input:focus-visible,select:focus-visible,textarea:focus-visible{
  outline:2px solid var(--accent);outline-offset:1px}

/* Theme is a page-level setting, so it sits in the brand row rather than
   competing with four section tabs for 360px of nav. .btn already gives it a
   border and hover state -- this rule only fixes the circle's size and
   centers the icon inside it. */
#theme{margin-left:auto;align-self:center;display:flex;align-items:center;
  justify-content:center;width:2.5rem;height:2.5rem;padding:0;color:var(--soft)}
.badge{display:inline-block;min-width:1.15rem;margin-left:.35rem;padding:0 .3rem;
  background:var(--accent);color:var(--on-accent);border-radius:999px;font-size:.72rem;
  text-align:center}

.facet{margin-bottom:1.3rem}
.facet[data-facet="slot"]{display:none}
.facet h3{font-size:.85rem;font-weight:600;color:var(--soft);margin-bottom:.6rem}
.chips{display:flex;flex-wrap:wrap;gap:.45rem}
.chip{border:1px solid var(--rule);background:var(--paper);border-radius:999px;
  padding:.5rem 1rem;line-height:1.2;font-size:.9rem;cursor:pointer;color:var(--soft);
  transition:background .15s,border-color .15s,color .15s}
.chip.on{background:var(--accent-soft);border-color:var(--accent);color:var(--accent)}
.slider{display:flex;align-items:center;gap:.8rem}
.slider input{flex:1}
.sheet-foot{display:flex;gap:.6rem;justify-content:space-between;
  border-top:1px solid var(--rule);padding-top:.9rem;margin-top:.6rem}

.group{margin:2.4rem 0 .8rem;display:flex;align-items:baseline;gap:.6rem;
  border-bottom:1px solid var(--rule);padding-bottom:.5rem}
.group h2{font-size:1.05rem;font-weight:600;color:var(--accent)}
.group em{font-style:normal;font-size:.85rem;color:var(--soft)}
ul.list{list-style:none;margin:0;padding:0}
ul.list li{border-bottom:1px solid var(--rule)}
/* A list row is title / macro / meta. On a phone the title takes the whole
   width and the macro drops onto the meta line -- squeezing it into a right
   column wrapped nearly every title onto two lines. Wide enough, and the macro
   returns to its right-aligned column where a sorted list can be scanned. */
ul.list a{display:flex;flex-wrap:wrap;align-items:baseline;gap:.2rem .6rem;
  padding:.9rem .3rem;border-radius:9px;transition:background .15s}
ul.list a:hover{background:var(--card)}
ul.list a .t{flex:1 0 100%;font-size:1.05rem;font-weight:500}
ul.list a .macro{order:2}
ul.list a .meta{order:3;flex:1;margin-top:0}
/* The macro is the payload -- the number a household actually scans for --
   so it reads in ink at full weight, not muted into the meta line beneath it. */
.macro{white-space:nowrap;font-size:.92rem;font-weight:600;color:var(--ink);
  font-variant-numeric:tabular-nums}
.meta{font-size:.85rem;color:var(--soft);margin-top:.25rem;line-height:1.5}
.dot{display:inline-block;width:.42rem;height:.42rem;border-radius:50%;
  vertical-align:.06rem;margin-right:.3rem}
.dot.in{background:var(--in)} .dot.under{background:var(--under)} .dot.over{background:var(--over)}
.empty{color:var(--soft);padding:3rem 0;text-align:center;font-style:italic}

.back{display:inline-block;font-size:.9rem;color:var(--soft);margin-bottom:1rem}
.back:hover{color:var(--accent)}
article h2{font-family:var(--serif);font-size:clamp(1.5rem,1.15rem + 1.6vw,2rem);
  line-height:1.2;margin-bottom:.4rem}
.tagline{font-size:.88rem;color:var(--soft);margin-bottom:1.6rem;line-height:1.6}
section{margin:2.2rem 0}
section > h3{font-size:1.05rem;font-weight:600;color:var(--accent);
  border-bottom:1px solid var(--rule);padding-bottom:.5rem;margin-bottom:1rem}
table{width:100%;border-collapse:collapse;font-size:.92rem}
th{text-align:left;font-weight:600;font-size:.8rem;color:var(--soft);
  padding:.5rem .8rem;border-bottom:1px solid var(--rule)}
td{padding:.65rem .8rem;border-bottom:1px solid var(--rule);vertical-align:top}
th:first-child,td:first-child{padding-left:0}
th:last-child,td:last-child{padding-right:0}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.scroller{overflow-x:auto;-webkit-overflow-scrolling:touch}
ol.method{margin:0;padding-left:1.4rem}
ol.method li{margin-bottom:.85rem;line-height:1.6}
.note{font-size:.85rem;color:var(--soft);line-height:1.5}
.warn{border-left:3px solid var(--accent);background:var(--accent-soft);
  border-radius:0 var(--radius) var(--radius) 0;
  padding:.8rem 1rem;font-size:.9rem;line-height:1.55;margin:.8rem 0}
.flag{color:var(--over);font-size:.82rem;font-weight:600}
.pill{display:inline-block;border:1px solid var(--rule);border-radius:999px;
  padding:.15rem .7rem;font-size:.8rem;color:var(--soft);margin:0 .3rem .3rem 0}
.pill.un{border-color:var(--accent);color:var(--accent)}
.day{border-bottom:1px solid var(--rule);padding:1.1rem 0}
.day h4{margin:0 0 .55rem;font-size:.9rem;font-weight:600;color:var(--soft);
  display:flex;flex-wrap:wrap;gap:.2rem .8rem;
  justify-content:space-between;align-items:baseline}
.day h4 span:first-child{color:var(--ink)}
.day dl{margin:0;display:grid;grid-template-columns:5.6rem 1fr;gap:.35rem .7rem}
.day dt{font-size:.8rem;color:var(--soft);text-transform:capitalize}
.day dd{margin:0;font-size:.95rem}
/* Today's card is the page's answer to "what am I cooking tonight" -- the
   thing the household actually opens the page for, so it is the one place the
   two daily numbers get to be the biggest text on the page rather than a
   line of muted meta. */
.day.now{border:1px solid var(--rule);border-left:4px solid var(--accent);
  background:var(--card);border-radius:var(--radius);
  padding:1.5rem 1.6rem;margin-bottom:2.2rem;box-shadow:0 1px 3px var(--shade)}
.day.now h4{font-family:var(--serif);font-size:1.15rem;color:var(--accent);font-weight:600}
.day.now dl{gap:.6rem .7rem}
.day.now dd{font-size:1.1rem}
.stats{display:flex;gap:clamp(1.6rem,5vw,2.6rem);flex-wrap:wrap;margin:1rem 0 1.4rem}
.stat{display:flex;flex-direction:column}
.stat b{font-family:var(--serif);font-weight:600;line-height:1;color:var(--ink);
  font-size:clamp(1.9rem,1.5rem + 1.6vw,2.4rem);font-variant-numeric:tabular-nums}
.stat span{font-size:.82rem;color:var(--soft);margin-top:.35rem}
.stat.flag b{color:var(--over)}
/* A meal in the day grid is the way into its Recipe, so it has to read as a
   link -- the global bare `a` would leave it looking like plain text. */
.day dd a,.tagline a{color:var(--accent)}
.day dd a{border-bottom:1px solid var(--accent-soft)}
/* Plan mode. The drawer is its own thing, not a reused .sheet -- .sheet turns
   into a sticky sidebar on wide screens and this must stay at the bottom. */
.drawer{position:fixed;inset:auto 0 0 0;z-index:40;background:var(--card);
  border-top:1px solid var(--rule);box-shadow:0 -2px 14px var(--shade);
  padding:.85rem 0}
.drawer .wrap{display:flex;align-items:center;gap:.7rem;flex-wrap:wrap}
.drawer .where{font-size:1rem}
.drawer .where b{text-transform:capitalize}
.drawer .rest{margin-left:auto;display:flex;gap:.6rem}
body.plan-on{padding-bottom:6.5rem}
body.plan-on .list a{cursor:pointer}
body.plan-on .list a:hover{background:var(--accent-soft)}
body.plan-on .list a:hover .t{color:var(--accent)}
button[disabled]{opacity:.45;cursor:not-allowed}
button[disabled]:hover{border-color:var(--rule)}
textarea{width:100%;font:inherit;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
  font-size:.85rem;line-height:1.6;color:inherit;background:var(--card);
  border:1px solid var(--rule);border-radius:9px;padding:.85rem}
.subnav{display:flex;gap:1.2rem;margin-bottom:1.3rem;font-size:.9rem}
.subnav a{color:var(--soft);border-bottom:1px solid transparent;padding-bottom:.2rem}
.subnav a.on{color:var(--accent);border-bottom-color:var(--accent)}

@media(max-width:991.98px){
  #sheet{--bs-offcanvas-height:78vh}
}
@media(min-width:992px){
  body{font-size:17.5px}
  .layout{display:grid;grid-template-columns:15rem 1fr;gap:2.5rem;align-items:start}
  /* .offcanvas-lg already goes static and undecorated at this width -- this
     adds back the one thing it doesn't do on its own: staying in view while
     the list scrolls past it. */
  #sheet{position:sticky;top:6.4rem;border:1px solid var(--rule);
    border-radius:var(--radius);padding:1.1rem}
  #sheet .offcanvas-body{display:block}
  #filterbtn{display:none}
  .quickbar{display:none}
  .facet[data-facet="slot"]{display:block}
  .day dl{grid-template-columns:6.5rem 1fr}
  ul.list a .t{flex:1 1 auto}
  ul.list a .macro{margin-left:auto}
  ul.list a .meta{flex:1 0 100%}
}
</style>

</head>
<body>
<nav class="navbar navbar-expand sticky-top border-bottom bg-body py-0">
  <div class="wrap d-flex flex-wrap align-items-center w-100">
    <div class="brand"><h1>Meal Planning</h1><span>plan the week, buy it once</span>
      <button id="theme" type="button" class="btn btn-sm rounded-circle"></button></div>
    <div id="nav" class="navbar-nav d-flex flex-row flex-wrap"></div>
  </div>
</nav>
<main class="wrap"><div id="app"></div></main>
<div class="drawer" id="drawer" hidden></div>

<script id="data" type="application/json">__PAYLOAD__</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const byslug = Object.fromEntries(D.recipes.map(r => [r.slug, r]));
/* The household's week starts Monday; D.days starts Sunday because that is the
   order a Plan's grid is written in. */
const WEEK = D.days.slice(1).concat(D.days.slice(0, 1));
const SLOT_COUNT = D.days.length * D.slots.length;
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

let route = {view:'today', slug:null, sub:null, f:{}, q:'', min:0, sort:'title'};

function readHash(){
  const raw = location.hash.replace(/^#/,'');
  const [path, query] = raw.split('?');
  const parts = (path || 'today').split('/');
  const r = {view: parts[0] || 'today', slug: parts[1] || null, sub: null,
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
  if (r.view === 'recipe' || r.view === 'plan') path += '/' + r.slug;
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
  /* `planmode` is the wizard toggle, not a view -- `plan` is a Plan's own page. */
  const tabs = [['today','Today'],['recipes','Recipes'],['plans','Plans'],
                ['orders','Orders'],['planmode','Plan']];
  const here = route.view === 'recipe' ? 'recipes'
             : route.view === 'plan' ? 'plans' : route.view;
  document.getElementById('nav').innerHTML = tabs.map(([v,label]) =>
    v === 'planmode'
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
  const rows = FACETS.map(k => `<div class="facet" data-facet="${k}"><h3>${k}</h3><div class="chips">` +
    D.facets[k].map(v => {
      const on = (route.f[k]||[]).includes(v);
      return `<button class="chip ${on?'on':''}" data-facet="${k}" data-value="${v}">${nice(v)}</button>`;
    }).join('') + `</div></div>`).join('');
  return `<div class="offcanvas-bottom offcanvas-lg" data-bs-scroll="true" tabindex="-1" id="sheet">
    <div class="offcanvas-header">
      <h2 class="h6 mb-0">Filters</h2>
      <button class="btn-close" id="done" aria-label="Close"></button>
    </div>
    <div class="offcanvas-body">
    ${rows}
    <div class="facet"><h3>Protein floor</h3><div class="slider">
      <input type="range" class="form-range" id="min" min="0" max="60" step="5" value="${route.min}">
      <span class="macro" id="minlabel">${route.min ? g(route.min)+'+' : 'any'}</span>
    </div></div>
    <div class="sheet-foot">
      <button class="btn btn-outline-secondary" id="clear">Clear all</button>
    </div>
    </div></div>`;
}

function quickbar(){
  const on = v => (route.f.slot||[]).includes(v);
  return `<div class="quickbar">${D.facets.slot.map(v =>
    `<button class="chip ${on(v)?'on':''}" data-facet="slot" data-value="${v}">${nice(v)}</button>`
  ).join('')}</div>`;
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
      <span class="t">${esc(r.title)}</span>
      <span class="macro">${scoreDot('protein',r)}${g(r.protein_g)} · ${kc(r.kcal)} kcal</span>
      <span class="meta">${[star(r.rating), nice(r.protein), r.effort ? r.effort+' effort' : '',
        (r.appliances||[]).map(nice).join(', ') || 'no appliance',
        (r.tags||[]).map(nice).join(', ')].filter(Boolean).join(' · ')}</span>
    </a></li>`).join('')}</ul>`).join('')
    : `<p class="empty">No Recipe matches those filters.</p>`;

  const n = activeCount();
  return `<p class="lede">${D.recipes.length} Recipes. Showing ${hits.length}.</p>
    <div class="tools">
      <input type="search" id="q" class="form-control" placeholder="Search recipes"
             title="Searches titles, ingredients, Pinned products and method"
             value="${esc(route.q)}">
      <select id="sort" class="form-select" aria-label="Sort within each Slot" style="flex:0 1 auto">${
        Object.entries(SORTS).map(([k,v]) =>
          `<option value="${k}"${k === route.sort ? ' selected' : ''}>${v.label}</option>`
        ).join('')}</select>
      <button id="filterbtn" class="btn btn-outline-secondary" type="button"
              data-bs-toggle="offcanvas" data-bs-target="#sheet" aria-controls="sheet">
        Filters${n ? `<span class="badge">${n}</span>` : ''}</button>
    </div>
    ${quickbar()}
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
  </article>`;
}

function planList(){
  if (!D.plans.length) return `<p class="empty">No week has been planned yet.</p>`;
  return `<p class="lede">${D.plans.length} planned week${D.plans.length>1?'s':''},
    latest first. A Plan is one real week — Recipes swapped, days away, Slots
    eaten out.</p>
    <ul class="list">${D.plans.map(p=>`<li><a href="#plan/${p.slug}">
      <span class="t">${esc(p.title)}</span>
      <span class="macro">${p.cooked} / ${SLOT_COUNT} cooked</span>
      <span class="meta">${SLOT_COUNT - p.cooked
        ? (SLOT_COUNT - p.cooked) + ' Slot(s) eaten out'
        : 'every Slot cooked at home'}</span>
    </a></li>`).join('')}</ul>`;
}

/* One day of a Plan. Today is the same block lifted out and marked `.now`,
   which is why this is a function and not two copies of the markup. */
function dayBlock(p, day, cls, label){
  const t = p.totals[day];
  const cells = D.slots.map(s => {
    const value = p.days[day][s];
    const r = byslug[value];
    return `<dt>${s}</dt><dd>${r
      ? `<a href="#recipe/${r.slug}">${esc(r.title)}</a>
         <span class="note">${g(r.protein_g)}</span>`
      : `<span class="note">${value === 'eaten-out' ? 'eaten out' : '—'}</span>`}</dd>`;
  }).join('');
  // The hero card (`.now`, today's own card) gets the day's two numbers as a
  // stat row -- the biggest text on the page, because it's the answer the
  // household actually opened the page for. Every other day keeps them as a
  // quiet macro line; showing both would just repeat the same two figures.
  const hero = cls === 'now' && t.cooked;
  const headMacro = hero ? '' : t.cooked
    ? `${g(t.protein_g)} · ${kc(t.kcal)} kcal ${
        t.flags.length ? `<span class="flag">↓${t.flags.join(' ')}</span>` : ''}`
    : 'nothing cooked at home';
  const stats = hero ? `<div class="stats">
      <div class="stat"><b>${g(t.protein_g)}</b><span>protein</span></div>
      <div class="stat"><b>${kc(t.kcal)}</b><span>kcal</span></div>
      ${t.flags.length ? `<div class="stat flag"><b>↓</b><span>${t.flags.join(' &amp; ')}</span></div>` : ''}
    </div>` : '';
  return `<div class="day${cls ? ' ' + cls : ''}"><h4><span>${esc(label || cap(day))}</span>
    ${headMacro ? `<span class="macro">${headMacro}</span>` : ''}</h4>
    ${stats}<dl>${cells}</dl></div>`;
}

/* The Monday of the week containing `d`, as YYYY-MM-DD in local time -- a Plan
   is named for its Monday, and toISOString would shift the date across
   midnight for anyone west of Greenwich. */
function mondayISO(d){
  const x = new Date(d.getFullYear(), d.getMonth(), d.getDate() - ((d.getDay() + 6) % 7));
  const pad = n => String(n).padStart(2,'0');
  return x.getFullYear() + '-' + pad(x.getMonth()+1) + '-' + pad(x.getDate());
}

/* What am I cooking tonight, and where is that Recipe. The page's most-asked
   question, so it is the page's front door. The week is resolved from the
   clock in the reader's hand, never baked in at generation time -- the page is
   committed and would otherwise be wrong by Tuesday. */
function todayView(){
  const now = new Date();
  const week = mondayISO(now);
  const p = D.plans.find(x => x.slug === week) || D.plans[0];
  const stale = p.slug !== week;
  const day = D.days[now.getDay()];
  const date = now.toLocaleDateString('en-GB', {weekday:'long', day:'numeric', month:'long'});
  const rest = (stale ? WEEK : WEEK.filter(d => d !== day))
                 .map(d => dayBlock(p, d)).join('');

  return `<p class="lede">${esc(date)} · <a href="#plan/${p.slug}">${esc(p.title)}</a></p>
    ${stale
      ? `<div class="warn">No Plan covers this week. Showing the latest,
          <strong>${esc(p.title)}</strong> — <code>plan-the-week</code> writes the next one.</div>`
      : dayBlock(p, day, 'now', 'Today — ' + cap(day))}
    <section><h3>${stale ? 'The week' : 'The rest of the week'}</h3>${rest}</section>`;
}

function planDetail(slug){
  const p = D.plans.find(x => x.slug === slug);
  if (!p) return `<p class="empty">No Plan called ${esc(slug)}.</p>`;
  const days = WEEK.map(day => dayBlock(p, day)).join('');

  return `<a class="back" href="#plans">← Plans</a>
  <article><h2>${esc(p.title)}</h2>
    <p class="tagline">${p.cooked} of ${SLOT_COUNT} Slots cooked at home</p>

    <section><h3>The week</h3>
      <p class="note">Tap a meal to open its Recipe. Day totals are summed from the
        Recipes each Slot names; a day with nothing cooked at home is not measured
        against the goals, and a Plan is never checked against a layout —
        a real week deviates on purpose. Floor ${g(D.goals.protein_floor)}/day,
        ceiling ${kc(D.goals.kcal_ceiling)} kcal/day.</p>
      ${days}</section>
  </article>`;
}

/* Plan mode. The pool stays on screen and the wizard walks: the drawer names
   one Slot, a click on a Recipe fills it and advances. Selections live here for
   the session only -- the page is generated, not an app, and a refresh starting
   clean is honest where a stale grid would not be. */
const PLAN_SEQ = WEEK.flatMap(day => D.slots.map(slot => [day, slot]));
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
      into <code>plan-the-week</code> at step 2, where a Plan's grid starts.</p>
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
  /* Today has nothing to say before the first Plan exists; the pool does. */
  const v = (route.view === 'today' && !D.plans.length) ? 'recipes' : route.view;
  app.innerHTML =
      checkedOut    ? checkoutView()
    : v === 'today'  ? todayView()
    : v === 'recipe' ? recipeDetail(route.slug)
    : v === 'plans'  ? planList()
    : v === 'plan'   ? planDetail(route.slug)
    : v === 'orders' ? ordersView()
    : recipeList();
  renderDrawer();
  if (checkedOut) wireCheckout();
  else if (v === 'recipes' || v === undefined) { wireFilters(); wirePlanClicks(); }
  window.scrollTo(0, 0);
}

function wireFilters(){
  const sheet = document.getElementById('sheet');
  const wide = () => matchMedia('(min-width:992px)').matches;
  /* getOrCreateInstance, not `new` -- recipeList() rebuilds #sheet's markup
     from scratch on every render(), so any instance tied to the previous
     node is already gone with it. Bootstrap tracks the instance on the DOM
     node itself, so asking for "the instance for this node, creating one if
     there isn't one yet" is always correct, whether this is the first
     render or the fiftieth. */
  const offcanvas = () => bootstrap.Offcanvas.getOrCreateInstance(document.getElementById('sheet'));
  const isShown = () => sheet.classList.contains('show');

  document.getElementById('done').onclick = () => offcanvas().hide();

  const q = document.getElementById('q');
  let timer;
  q.oninput = () => { clearTimeout(timer); timer = setTimeout(() => {
    route.q = q.value; writeHash(route, true);
    const at = q.selectionStart; render();
    const nq = document.getElementById('q'); nq.focus(); nq.setSelectionRange(at, at);
  }, 180); };

  const sort = document.getElementById('sort');
  sort.onchange = () => { route.sort = sort.value; writeHash(route, true); render(); };

  document.querySelectorAll('.chip').forEach(chip => chip.onclick = () => {
    const {facet, value} = chip.dataset;
    const cur = new Set(route.f[facet] || []);
    cur.has(value) ? cur.delete(value) : cur.add(value);
    route.f[facet] = [...cur];
    if (!route.f[facet].length) delete route.f[facet];
    writeHash(route, true); const wasOpen = isShown();
    render(); if (wasOpen && !wide()) offcanvas().show();
  });

  const min = document.getElementById('min');
  min.oninput = () => { document.getElementById('minlabel').textContent =
    +min.value ? '~' + min.value + 'g+' : 'any'; };
  min.onchange = () => { route.min = +min.value; writeHash(route, true);
    const wasOpen = isShown(); render();
    if (wasOpen && !wide()) offcanvas().show(); };

  document.getElementById('clear').onclick = () => {
    route.f = {}; route.q = ''; route.min = 0; writeHash(route, true); render(); };
}

/* Theme toggle. Two states, not three: the stored value IS the override and
   its absence means "follow the system", so there is no separate Auto to
   explain. The icon shows the theme you would switch TO. The button lives in
   the static header, so it is wired once and survives every render(). */
const ICON = {
/* Keyed by the theme the icon OFFERS, not the one it depicts: a moon means
   "go dark", so it is what you see while light. */
  dark: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"'
      + ' stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
      + '<path d="M20.5 14.3A8.5 8.5 0 0 1 9.7 3.5a8.5 8.5 0 1 0 10.8 10.8z"/></svg>',
  light: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"'
      + ' stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
      + '<circle cx="12" cy="12" r="4.2"/><path d="M12 2.6v2.1M12 19.3v2.1M4.2 4.2l1.5 1.5'
      + 'M18.3 18.3l1.5 1.5M2.6 12h2.1M19.3 12h2.1M4.2 19.8l1.5-1.5M18.3 5.7l1.5-1.5"/></svg>',
};

/* Both attributes always move together -- data-theme drives the page's own
   13 variables, data-bs-theme drives Bootstrap's. One setter, so nothing can
   set one and forget the other. */
function setTheme(value){
  document.documentElement.dataset.theme = value;
  document.documentElement.dataset.bsTheme = value;
}

function paintTheme(){
  const dark = document.documentElement.dataset.theme === 'dark';
  const btn = document.getElementById('theme');
  btn.innerHTML = dark ? ICON.light : ICON.dark;
  const label = dark ? 'Switch to the light theme' : 'Switch to the dark theme';
  btn.setAttribute('aria-label', label);
  btn.title = label;
}

document.getElementById('theme').onclick = () => {
  const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  setTheme(next);
  try { localStorage.setItem('theme', next); } catch (e) {}
  paintTheme();
};

/* Until the reader has chosen, the system keeps the casting vote -- including
   when it changes at dusk with the page still open. */
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
  let saved = null;
  try { saved = localStorage.getItem('theme'); } catch (e) {}
  if (saved) return;
  setTheme(event.matches ? 'dark' : 'light');
  paintTheme();
});

paintTheme();
addEventListener('hashchange', () => { route = readHash(); render(); });
route = readHash();
render();
</script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI"
        crossorigin="anonymous"></script>
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
        f"{len(payload['plans'])} Plans, {len(payload['orders'])} orders, "
        f"{len(payload['aggregate'])} distinct items, {len(html)} bytes."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Failure as exc:
        print(f"browse: {exc}", file=sys.stderr)
        sys.exit(1)
