#!/usr/bin/env python3
"""Generate a Plan's shopping section.

The only code in this repo, authorised by
.scratch/meal-planning-system/issues/08-what-the-four-skills-are.md.

Reads PINS.md, Recipes/ and a Plan (or a Menu -- the grids are identical),
aggregates every ingredient across the resolved grid, divides into packs,
splits by store, drops Staples, and prints the shopping section to stdout.
The shopping-list skill writes that output into the Plan.

Usage: bin/shopping-list.py Plans/2026-09-07.md
"""

import math
import os
import re
import sys

import yaml

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
SLOTS = ["breakfast", "lunch", "dinner", "pudding"]

# A Slot the household did not cook. Keeps the grid at 28 so the completeness
# check still means something, and contributes nothing to the list.
EATEN_OUT = "eaten-out"

# Units that measure an amount rather than count a container. A Pin whose own
# unit is one of these cannot be divided by a pack sold in the other, so a
# gram total against a millilitre pack is flagged, never converted.
MEASURED = {"g", "ml"}

STORES = [
    ("waitrose", "Waitrose"),
    ("soutars", "Soutars"),
    ("dorset-meats", "Dorset Meats"),
]

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


class Failure(Exception):
    """A violation that makes the sum meaningless. Stop; do not emit a list."""


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_frontmatter(path):
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as exc:
        raise Failure(f"cannot read {path}: {exc}")
    match = FRONTMATTER.match(text)
    if not match:
        raise Failure(f"{path} has no frontmatter block")
    return yaml.safe_load(match.group(1))


def load_pins(root):
    text = open(os.path.join(root, "PINS.md"), encoding="utf-8").read()
    blocks = re.findall(r"```yaml\n(.*?)```", text, re.S)
    if not blocks:
        raise Failure("PINS.md contains no yaml catalogue block")
    return yaml.safe_load(blocks[0])


def load_grid(path):
    """Return the 28 Slots as (day, slot, value), hard-failing on an incomplete grid."""
    front = load_frontmatter(path)
    days = front.get("days")
    if not isinstance(days, dict):
        raise Failure(f"{path} has no days: grid")

    grid = []
    missing = []
    for day in DAYS:
        entry = days.get(day)
        if not isinstance(entry, dict):
            missing.extend(f"{day}/{slot}" for slot in SLOTS)
            continue
        for slot in SLOTS:
            value = entry.get(slot)
            if not value:
                missing.append(f"{day}/{slot}")
            else:
                grid.append((day, slot, value))

    if missing:
        raise Failure(
            f"{path} is not 28 complete Slots -- {len(missing)} empty: "
            + ", ".join(missing)
        )
    return front, grid


def load_recipes(root, grid):
    """Load every Recipe the grid names. A slug resolving to no file is fatal."""
    recipes = {}
    orphans = []
    for _, _, value in grid:
        if value == EATEN_OUT or value in recipes:
            continue
        path = os.path.join(root, "Recipes", f"{value}.md")
        if not os.path.isfile(path):
            orphans.append(value)
            continue
        recipes[value] = load_frontmatter(path)
    if orphans:
        raise Failure(
            "slug resolves to no Recipe file: " + ", ".join(sorted(set(orphans)))
        )
    return recipes


def check_rule(recipes, pins):
    """Every ingredient line uses its Pin's unit, or is an unquantified Staple."""
    violations = []
    for slug, recipe in sorted(recipes.items()):
        for line in recipe.get("ingredients", []):
            key = line["ingredient"]
            pin = pins.get(key)
            if pin is None:
                continue  # Unpinned -- reported as a list, not an error
            if line.get("unit") == pin.get("unit"):
                continue
            if "qty" not in line and pin.get("staple"):
                continue
            if "qty" not in line:
                violations.append(
                    f"{slug}: {key} has no qty and its Pin is not a Staple"
                )
            else:
                violations.append(
                    f"{slug}: {key} is {line.get('unit')!r}"
                    f" against Pin unit {pin.get('unit')!r}"
                )
    if violations:
        raise Failure(
            "Recipe/Pin rule violated -- the sum would be meaningless:\n  "
            + "\n  ".join(violations)
        )


def aggregate(grid, recipes):
    """Sum each ingredient across the resolved grid. Addition only, no conversion."""
    totals = {}
    quantified = set()
    uses = 0
    for _, _, value in grid:
        if value == EATEN_OUT:
            continue
        for line in recipes[value].get("ingredients", []):
            uses += 1
            key = line["ingredient"]
            totals.setdefault(key, 0)
            if "qty" in line:
                totals[key] += line["qty"]
                quantified.add(key)
    return totals, quantified, uses


def number(value):
    return f"{value:g}"


def pack_label(pack):
    return f"{number(pack['qty'])} {pack['unit']}"


def divide(total, pin):
    """How many packs to buy, plus a flag when the pack cannot be divided into."""
    pack = pin.get("pack")
    if not pack:
        return 1, "buy 1", "pack unknown"

    unit, pack_unit = pin.get("unit"), pack.get("unit")
    if unit == pack_unit:
        count = math.ceil(total / pack["qty"])
        return count, f"{count} × {pack_label(pack)}", None

    if unit not in MEASURED:
        # A countable container: one `can` is one pack of 410g.
        count = math.ceil(total)
        return count, f"{count} × {unit} ({pack_label(pack)})", None

    return 1, "buy 1", f"pack unit mismatch ({unit} vs {pack_unit})"


def humanise(slug):
    return slug.replace("-", " ").capitalize()


def build(totals, quantified, pins):
    """Sort every summed ingredient into a store, the Staples bin, or Unpinned."""
    shoppable = {store: [] for store, _ in STORES}
    staples = []
    unpinned = []

    for key, total in totals.items():
        pin = pins.get(key)
        if pin is None:
            unpinned.append(key)
            continue
        if pin.get("staple"):
            staples.append(key)
            continue
        if key not in quantified:
            # A non-staple with no qty cannot happen: check_rule rejects it.
            raise Failure(f"{key} is a non-staple with no quantity")

        store = pin.get("store")
        if store not in shoppable:
            raise Failure(f"{key} has unknown store {store!r}")

        row = {
            "display": pin.get("display", humanise(key)),
            "need": f"{number(total)} {pin.get('unit')}",
            "line_number": pin.get("line_number"),
            "search_term": pin.get("search_term"),
        }
        if store == "waitrose":
            _, buy, flag = divide(total, pin)
            row["buy"] = buy
            row["flag"] = flag
        shoppable[store].append(row)

    for rows in shoppable.values():
        rows.sort(key=lambda r: r["display"].lower())
    return shoppable, sorted(staples), sorted(unpinned)


def render(source, front, grid, shoppable, staples, unpinned):
    out = []
    lines = sum(len(rows) for rows in shoppable.values())
    eaten_out = sum(1 for _, _, v in grid if v == EATEN_OUT)

    out.append("## Shopping")
    out.append("")
    provenance = front.get("menu") or source
    summary = (
        f"Generated from `{provenance}`. **{lines} lines** across "
        f"{sum(1 for rows in shoppable.values() if rows)} stores, "
        f"**{len(unpinned)} to add by hand**, {len(staples)} Staples left out."
    )
    if eaten_out:
        summary += f" {eaten_out} Slot(s) eaten out."
    out.append(summary)

    for store, label in STORES:
        rows = shoppable[store]
        if not rows:
            continue
        out.append("")
        out.append(f"### {label} — {len(rows)} lines")
        out.append("")
        if store == "waitrose":
            out.append("| Item | Need | Buy | Line |")
            out.append("|---|---|---|---|")
            for r in rows:
                buy = r["buy"] + (f" ⚠ {r['flag']}" if r["flag"] else "")
                out.append(
                    f"| {r['display']} | {r['need']} | {buy} | {r['line_number'] or '—'} |"
                )
            out.append("")
            out.append("**Paste into Multi-search:**")
            out.append("")
            out.append("```")
            for r in rows:
                out.append(r["search_term"] or r["display"])
            out.append("```")
        else:
            out.append("| Item | Need |")
            out.append("|---|---|")
            for r in rows:
                out.append(f"| {r['display']} | {r['need']} |")

    out.append("")
    out.append(f"### Add by hand — {len(unpinned)} Unpinned")
    out.append("")
    if unpinned:
        out.append(
            "No Pin exists for these. Buying one puts it in your order history, "
            "where the next harvest turns it into a Pin."
        )
        out.append("")
        for key in unpinned:
            out.append(f"- {humanise(key)}")
    else:
        out.append("Every ingredient in this Plan is Pinned.")

    return "\n".join(out)


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2

    root = repo_root()
    pins = load_pins(root)
    front, grid = load_grid(argv[1])
    recipes = load_recipes(root, grid)
    check_rule(recipes, pins)
    totals, quantified, _ = aggregate(grid, recipes)
    shoppable, staples, unpinned = build(totals, quantified, pins)
    print(render(argv[1], front, grid, shoppable, staples, unpinned))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Failure as exc:
        print(f"shopping-list: {exc}", file=sys.stderr)
        sys.exit(1)
