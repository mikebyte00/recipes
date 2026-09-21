# Bootstrap 5 re-skin of the browse page

Branch: `bootstrap-reskin` (experiment — merges only if it earns it).

## Why

The browse page (`bin/browse.py` → `index.html`) is the household's phone
interface. Its mobile UI — a hand-rolled bottom sheet for filters, chip
toggles, a range slider — works but was built one component at a time as
needs came up. The ask: swap the hand-rolled layer for a mature component
library's out-of-the-box mobile behavior (focus trapping, backdrop, swipe
affordance) without changing what the page does or how it's generated.

## Decision this reverses

[Ticket 24](../../../.scratch/meal-planning-system/issues/24-browse-the-pool.md)
settled the page as **no server, no build step, no runtime fetch** —
self-contained, working from `file://` or offline. Loading Bootstrap from a
CDN breaks that: the page needs network access to render and behave
correctly. Ticket 24 is amended (commit on this branch) to narrow the rule to
**no fetch of the page's own data** — `bin/browse.py`'s JSON payload stays
fully inlined; only a UI library is fetched at runtime. If this branch
doesn't ship, that amendment doesn't reach `main` either.

**Options considered and rejected:** vendoring Bootstrap's files into the
repo (keeps zero runtime fetch, but the user chose the CDN + amend-the-ticket
path explicitly); staying vanilla (doesn't answer the "out of the box"
ask).

## Scope

Full re-skin: nav, tools row, filter sheet, chips, buttons, form controls,
recipe list, Plan-mode wizard bar. Not in scope: any change to what
`bin/browse.py` parses, computes, or redacts — this touches only the
`<style>` block and the HTML/class names the JS templates emit.

## Theming

**Keep the page's own palette**, not Bootstrap's defaults — validated
against a side-by-side mockup during brainstorming. The existing 13 custom
properties (`--paper`, `--card`, `--ink`, `--soft`, `--rule`, `--accent`,
`--accent-soft`, `--under`, `--over`, `--in`, `--on-accent`, `--shade`,
`--scrim`) stay as the source of truth in both `:root` and
`:root[data-theme=dark]`. Both blocks gain Bootstrap variable overrides
mapping onto them, e.g.:

```css
:root{
  /* existing --paper/--card/--ink/... unchanged */
  --bs-body-bg: var(--paper);
  --bs-body-color: var(--ink);
  --bs-border-color: var(--rule);
  --bs-primary: var(--accent);
  --bs-primary-rgb: /* rgb() of --accent, computed once, not var()-able */;
  --bs-secondary-color: var(--soft);
  --bs-focus-ring-color: var(--shade);
}
```

(`--bs-*-rgb` variables can't reference a hex custom property directly —
Bootstrap's components that need the RGB triple, e.g. focus rings, take the
literal computed value. List every `--bs-*-rgb` this actually requires once
components are wired, rather than pre-computing ones nothing reads.)

**The theme boot script is unchanged in its decision logic** — the 7 `node`
tests in `tests/test_browse.py` cover exactly that logic and must keep
passing unmodified. It gains one line: whatever value it stamps as
`data-theme` on `<html>`, it also stamps as `data-bs-theme`, so Bootstrap's
own color-mode CSS activates in step with the existing one.

## Component mapping

| Current | Bootstrap replacement | Notes |
|---|---|---|
| `.sheet` (Filters bottom panel) + `.scrim` | `Offcanvas`, bottom placement, responsive via `.offcanvas-lg` | Offcanvas ships its own backdrop — `.scrim` and the manual `open()`/hidden-attribute toggling in `wireFilters()` are replaced by Bootstrap's JS API. **Breakpoint moves from the page's custom `56rem` (896px) to Bootstrap's fixed `lg` step (992px)**, decided during plan-writing: `.offcanvas-lg`'s sidebar/overlay split only happens at Bootstrap's own grid breakpoints, and retuning them needs a Sass build this project doesn't have. The page's other `@media(min-width:56rem)` rules (nav, list column layout) move to `992px` too, so there's one breakpoint, not two. |
| `.drawer` (Plan-mode wizard bar) | `.fixed-bottom` + `.shadow` utilities | Always-visible during Plan mode, never collapses — no JS component, just repositioned with utility classes |
| `.chip` toggle buttons (Slot quickbar + facet panel) | Stays a custom `.chip` class, restyled onto Bootstrap variables | No Bootstrap primitive fits multi-select toggle pills cleanly; `btn-check` groups are single-select-shaped |
| `<select id="sort">`, `<input type=range id="min">` | `.form-select`, `.form-range` | |
| `<input type=search id="q">` | `.form-control` | |
| Buttons (`#filterbtn`, `#done`, `#clear`, theme toggle) | `.btn.btn-outline-*` | |
| Top `nav` (`Today · Recipes · Plans · Orders · Plan`) | Bootstrap `navbar` + `nav-link` | 5 items fit one row at phone width already — no `navbar-toggler` collapse needed |
| Recipe list rows (`ul.list`) | `list-group` / `list-group-item` | |
| Active-filter count badge | `.badge` | |

## Loading

Bootstrap 5.3's CSS + JS bundle (bundle build includes Popper — not needed by
Offcanvas itself, but needed if a future component, e.g. a tooltip, wants
it) from a CDN (jsDelivr), pinned to an exact patch version with
Subresource Integrity hashes. No build step, no bundler; two new tags,
matching the page's existing "one generated file, nothing else" model.

**The exact version string and SRI hashes are resolved at implementation
time** (verify against jsDelivr's/npm's current 5.3.x release), not
hardcoded here from a stale knowledge cutoff.

## Testing & verification

- `tests/test_browse.py`'s 59 tests must keep passing unmodified in
  substance — none assert on CSS class names or markup shape today, so this
  re-skin shouldn't need new test code, only re-running the existing suite
  (including the 7 `node` theme-boot-script tests, since that script gains a
  line).
- `bin/browse.py --check` must report clean after regenerating.
- Manual pass in a real mobile viewport: open the Filters Offcanvas, toggle
  a Slot chip, enter Plan mode and confirm the wizard bar still reads
  correctly pinned to the bottom under Bootstrap's own CSS reset.
- Redaction tests are unaffected — they check the JSON payload and rendered
  order text, not styling.

## Non-goals

- No change to what `bin/browse.py` computes, parses, or redacts.
- No change to the hash-based router or any of the `route`/`matches`/`sorted`
  logic in the page's script.
- No offline/`file://` fallback for the CDN dependency — ticket 24's
  amendment accepts that degradation.
