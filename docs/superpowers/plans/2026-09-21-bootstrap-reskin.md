# Bootstrap 5 Re-skin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-skin `bin/browse.py`'s generated page onto Bootstrap 5 components (Offcanvas filter panel, navbar, list-group, form controls) while keeping the page's own cream/burnt-sienna palette, on the `bootstrap-reskin` branch.

**Architecture:** No new files, no build step. `bin/browse.py`'s `TEMPLATE` string gains two CDN tags (Bootstrap CSS+JS), gets its `<style>` block extended with `--bs-*` variable overrides, and has its HTML/JS template literals (`renderNav`, `facetPanel`, `quickbar`, `recipeList`, `wireFilters`, `renderDrawer`) edited in place to emit Bootstrap markup instead of the hand-rolled equivalents. `tests/test_browse.py` gains one new assertion (the theme boot script's `data-bs-theme` mirrors `data-theme`); its other 59 tests are not touched.

**Tech Stack:** Bootstrap 5.3.8 (CSS + JS bundle, includes Popper) via jsDelivr CDN, pinned with Subresource Integrity. No npm, no bundler — same "one generated `index.html`" model the page already uses.

**Spec:** [docs/superpowers/specs/2026-09-20-bootstrap-reskin-design.md](../specs/2026-09-20-bootstrap-reskin-design.md)

## Global Constraints

- **Palette stays the page's own**, not Bootstrap's defaults — the 13 existing custom properties (`--paper`, `--card`, `--ink`, `--soft`, `--rule`, `--accent`, `--accent-soft`, `--under`, `--over`, `--in`, `--on-accent`, `--shade`, `--scrim`) remain the source of truth; Bootstrap's `--bs-*` variables are overridden to point at them.
- **No fetch of the page's own data** — `bin/browse.py`'s inlined JSON payload is unchanged. Only the Bootstrap CSS/JS files are a runtime fetch (ticket 24's amendment already covers this).
- **The theme boot script's decision logic is unchanged** — it still decides `dark`/`light` from `localStorage` then system preference, exactly as the 7 `node` tests in `tests/test_browse.py` verify. It only gains a second attribute write.
- **The breakpoint is 992px, not the old `56rem` (896px)** — Bootstrap's `.offcanvas-lg` only breaks at its own fixed `lg` grid step, and retuning that needs a Sass build this project doesn't have. Every `@media(min-width:56rem)` rule in the page moves to `@media(min-width:992px)`.
- **Verification for markup/CSS-only tasks is regenerate + run the full suite + a manual visual check**, not a fabricated unit test — `tests/test_browse.py` deliberately asserts on data correctness and redaction, never on CSS class names or markup shape (confirmed by reading the file), and ticket 24 already establishes "run it against the real corpus and record the numbers" as this project's precedent for changes with no new logic. Only Task 2 (the theme boot script) has real new logic, and it gets a real failing-test-first cycle.
- **`.venv/bin/python`, not bare `python3`** — `bin/browse.py` needs PyYAML.
- **This branch does not merge itself.** The last task leaves `bootstrap-reskin` green and pushed; merging to `main` is a separate, later decision.

---

### Task 1: Load Bootstrap 5.3.8 from the CDN

**Files:**
- Modify: `bin/browse.py` (the `TEMPLATE` string's `<head>`, and just before `</body>`)

**Interfaces:**
- Produces: `.btn`, `.form-control`, `.form-select`, `.form-range`, `.navbar`, `.offcanvas`, `.list-group`, `.badge` and the rest of Bootstrap 5.3.8's CSS classes become usable in every later task. The global `bootstrap` JS object (`bootstrap.Offcanvas`, etc.) becomes available to the page's own `<script>` block, which runs after the bundle since it's the last `<script>` in `<body>`.

No functional change yet — nothing in the page uses a Bootstrap class or the `bootstrap` JS object until Task 3 onward. This task only proves the CDN load doesn't break anything and gives every later task something to build on.

- [ ] **Step 1: Add the CSS `<link>` right before the page's own `<style>` tag**

In `bin/browse.py`, find:

```python
<title>Meal Planning</title>
<!-- Before first paint, or the page flashes cream on the way to dark.
```

Change to:

```python
<title>Meal Planning</title>
<!-- Pinned to an exact patch release with Subresource Integrity: a compromised
     CDN response is rejected by the browser rather than executed. Ticket 24's
     amendment accepts this as the page's one runtime fetch -- everything else
     it needs is still the inlined JSON payload below. -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css"
      rel="stylesheet"
      integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB"
      crossorigin="anonymous">
<!-- Before first paint, or the page flashes cream on the way to dark.
```

- [ ] **Step 2: Add the JS bundle right before the closing `</body>`**

Find:

```python
paintTheme();
addEventListener('hashchange', () => { route = readHash(); render(); });
route = readHash();
render();
</script>
</body>
</html>
```

Change to:

```python
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
```

(The bundle loads *after* the page's own inline `<script>` runs, which is fine here — nothing in that inline script calls into `bootstrap.*` yet. Task 4 is the first task that does, and it runs from `wireFilters()`, which fires on every `render()`, well after page load.)

- [ ] **Step 3: Regenerate and verify nothing broke**

Run:
```bash
.venv/bin/python bin/browse.py
.venv/bin/python tests/test_browse.py
```
Expected: `index.html written: ...` then `Ran 59 tests ... OK`.

- [ ] **Step 4: Manual check**

Open `index.html` in a browser (or serve it locally). Confirm: the page looks visually identical to before (Bootstrap's CSS resets `margin`/`font` on elements the page doesn't yet use Bootstrap classes on — if anything shifted, it's almost certainly Bootstrap's `*, *::before, *::after{box-sizing:border-box}` or a base `body` font-family colliding; the page already sets both itself at higher specificity via its own `<style>` block, which loads *after* Bootstrap's, so it should win). Open devtools console: confirm no errors, and confirm `typeof bootstrap === 'object'`.

- [ ] **Step 5: Commit**

```bash
git add bin/browse.py index.html
git commit -m "Load Bootstrap 5.3.8 from jsDelivr, pinned with SRI

No markup uses it yet -- this only proves the CDN load doesn't
regress anything before later tasks build on it."
```

---

### Task 2: Sync `data-bs-theme` and remap Bootstrap's palette variables

**Files:**
- Modify: `bin/browse.py` (the theme boot script, the `#theme` click handler, the `matchMedia` change listener, both `:root` blocks)
- Modify: `tests/test_browse.py` (the `ThemeBootScript` harness)
- Modify: `CLAUDE.md` (test count, once the count changes)

**Interfaces:**
- Produces: every element on the page can read `--bs-body-bg`, `--bs-body-bg-rgb`, `--bs-body-color`, `--bs-body-color-rgb`, `--bs-emphasis-color`, `--bs-emphasis-color-rgb`, `--bs-secondary-color`, `--bs-secondary-color-rgb`, `--bs-tertiary-bg`, `--bs-tertiary-bg-rgb`, `--bs-border-color`, `--bs-border-color-translucent`, `--bs-primary`, `--bs-primary-rgb` and get the page's own palette instead of Bootstrap's blue-and-grey defaults. `<html>` always carries `data-bs-theme` equal to `data-theme`.

**This task has real new logic** (the boot script gains a line), so it gets a real red/green cycle, unlike the markup-only tasks around it.

- [ ] **Step 1: Extend the node harness to capture `data-bs-theme`, and add a failing test**

In `tests/test_browse.py`, find:

```python
HARNESS = """
const results = {};
for (const [saved, sysDark] of CASES) {
  globalThis.document = {documentElement: {dataset: {}}};
  globalThis.localStorage = {getItem() {
    if (saved === 'THROW') throw new Error('localStorage is denied here');
    return saved;
  }};
  globalThis.matchMedia = () => ({matches: sysDark});
  BOOT
  results[saved + '|' + sysDark] = document.documentElement.dataset.theme;
}
console.log(JSON.stringify(results));
"""
```

Replace with (capturing both attributes without touching the meaning of the existing `results` map, so the 7 existing assertions stay textually unmodified):

```python
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
```

Find:

```python
        try:
            out = subprocess.run([shutil.which("node"), path], check=True,
                                 capture_output=True, text=True).stdout
        finally:
            os.unlink(path)
        cls.themes = json.loads(out)
```

Replace with:

```python
        try:
            out = subprocess.run([shutil.which("node"), path], check=True,
                                 capture_output=True, text=True).stdout
        finally:
            os.unlink(path)
        data = json.loads(out)
        cls.themes = data["theme"]
        cls.bs_themes = data["bsTheme"]
```

Then add a new test method, right after `test_a_refusing_localstorage_still_renders_a_theme`:

```python
    def test_bs_theme_mirrors_theme(self):
        """Bootstrap's own color-mode CSS reads data-bs-theme, not data-theme
        -- the two must never disagree, in every one of the seven cases."""
        self.assertEqual(self.bs_themes, self.themes)
```

- [ ] **Step 2: Run the test to see it fail**

Run: `.venv/bin/python tests/test_browse.py ThemeBootScript`
Expected: `test_bs_theme_mirrors_theme` FAILs — `bsResults` values are all `undefined` (JSON-serialized as `null`) since the boot script doesn't set `dataset.bsTheme` yet. The other 6 `ThemeBootScript` tests still PASS (their assertions didn't change).

- [ ] **Step 3: Make the boot script set both attributes**

In `bin/browse.py`, find:

```python
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
})();
```

Replace with:

```python
  var theme = dark ? 'dark' : 'light';
  document.documentElement.dataset.theme = theme;
  document.documentElement.dataset.bsTheme = theme;
})();
```

- [ ] **Step 4: Run the test to see it pass**

Run: `.venv/bin/python tests/test_browse.py ThemeBootScript -v`
Expected: all 7 tests PASS, including `test_bs_theme_mirrors_theme`.

- [ ] **Step 5: Keep the live theme toggle and the system-preference listener in sync too**

The boot script only runs once, before first paint. The click handler and the `matchMedia` "change" listener both set `dataset.theme` again later, live — they need the same pairing or a manual toggle would leave `data-bs-theme` stuck at the boot-time value while `data-theme` (and the rest of the page) moves on.

In `bin/browse.py`, find:

```python
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
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem('theme', next); } catch (e) {}
  paintTheme();
};

/* Until the reader has chosen, the system keeps the casting vote -- including
   when it changes at dusk with the page still open. */
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
  let saved = null;
  try { saved = localStorage.getItem('theme'); } catch (e) {}
  if (saved) return;
  document.documentElement.dataset.theme = event.matches ? 'dark' : 'light';
  paintTheme();
});
```

Replace with:

```python
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
```

- [ ] **Step 6: Map Bootstrap's palette variables onto the page's own, in both `:root` blocks**

In `bin/browse.py`, find:

```python
:root{
  color-scheme:light;
  --paper:#faf7f1; --card:#fffdf9; --ink:#332f29; --soft:#6f675c;
  --rule:#e4dccf; --accent:#95462a; --accent-soft:#f2e5dd;
  --under:#9a6a1f; --over:#8d3a3a; --in:#4d6b45;
  --on-accent:#fff; --shade:rgba(60,45,25,.12); --scrim:rgba(50,40,28,.25);
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --radius:12px;
}
```

Replace with:

```python
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
```

Find:

```python
:root[data-theme=dark]{
  color-scheme:dark;
  --paper:#1a1714; --card:#221e19; --ink:#ece5da; --soft:#a49a8b;
  --rule:#3a332b; --accent:#e09468; --accent-soft:#3a2a20;
  --under:#d2a049; --over:#dd8585; --in:#8fbf7f;
  --on-accent:#1a1714; --shade:rgba(0,0,0,.5); --scrim:rgba(0,0,0,.55);
}
```

Replace with:

```python
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
```

- [ ] **Step 7: Regenerate and run the full suite**

Run:
```bash
.venv/bin/python bin/browse.py
.venv/bin/python tests/test_browse.py
```
Expected: `Ran 60 tests ... OK` (59 + the new `test_bs_theme_mirrors_theme`).

- [ ] **Step 8: Update the test count CLAUDE.md documents**

In `CLAUDE.md`, find:

```markdown
2. `.venv/bin/python tests/test_browse.py` — 59 tests, including the redaction
```

Replace with:

```markdown
2. `.venv/bin/python tests/test_browse.py` — 60 tests, including the redaction
```

- [ ] **Step 9: Manual check**

Open the page, toggle the theme button. Open devtools, run `document.documentElement.dataset` and confirm both `theme` and `bsTheme` are present and equal, in both the initial state and after clicking the toggle.

- [ ] **Step 10: Commit**

```bash
git add bin/browse.py tests/test_browse.py CLAUDE.md index.html
git commit -m "Sync data-bs-theme with data-theme and repoint Bootstrap's palette

Bootstrap's own --bs-* variables now resolve to this page's existing
13-variable palette instead of Bootstrap's blue-and-grey defaults, in
both the light and dark blocks. Every place that changes the theme
live (the boot script, the toggle, the system-preference listener)
sets both attributes through one setTheme() so they can't drift."
```

---

### Task 3: Nav → Bootstrap navbar

**Files:**
- Modify: `bin/browse.py` (the `<header>` markup, `renderNav()`, the `#theme` button CSS, `nav`/`.brand`/`header` CSS)

**Interfaces:**
- Consumes: `--bs-emphasis-color-rgb`, `--bs-body-bg` from Task 2.
- Produces: no change to `renderNav()`'s external behavior — same tabs, same `#plantoggle` toggle logic, same hash-based routing. Only the classes on the elements it renders change.

- [ ] **Step 1: Give the header Bootstrap's navbar scaffolding**

In `bin/browse.py`, find:

```python
<header><div class="wrap">
  <div class="brand"><h1>Meal Planning</h1><span>plan the week, buy it once</span>
    <button id="theme" type="button"></button></div>
  <nav id="nav"></nav>
</div></header>
```

Replace with:

```python
<nav class="navbar navbar-expand sticky-top border-bottom bg-body py-0">
  <div class="wrap d-flex flex-wrap align-items-center w-100">
    <div class="brand"><h1>Meal Planning</h1><span>plan the week, buy it once</span>
      <button id="theme" type="button" class="btn btn-sm rounded-circle"></button></div>
    <div id="nav" class="navbar-nav d-flex flex-row flex-wrap"></div>
  </div>
</nav>
```

(`renderNav()` fills `#nav` — it targeted `document.getElementById('nav')` before, which was a bare `<nav>` element; now it's a `<div id="nav">`, no JS change needed since `getElementById` doesn't care about tag name. The outer element is now the actual `<nav class="navbar">`, so there are no longer two nested `<nav>` tags. **`bg-body` is load-bearing, not decoration**: confirmed by reading the downloaded Bootstrap CSS that the bare `.navbar` class sets no `background-color` of its own — without `bg-body` (which resolves to `--bs-body-bg`, i.e. `--paper`, via Task 2) the sticky nav would be transparent, and anything with its own background scrolling underneath it (e.g. `.day.now`'s card, `.warn` blocks) would visibly show through the header while it's stuck to the top.)

- [ ] **Step 2: Drop the now-redundant custom header/nav positioning CSS, keep the rest**

In `bin/browse.py`, find:

```python
header{border-bottom:1px solid var(--rule);position:sticky;top:0;z-index:20;
  background:var(--paper)}
.brand{display:flex;align-items:center;gap:.7rem;padding:1.15rem 0 .7rem}
```

Replace with:

```python
.brand{display:flex;align-items:center;gap:.7rem;padding:1.15rem 0 .7rem}
```

(`.sticky-top`, `.border-bottom` and the navbar's own background-color -- via `--bs-body-bg`, which Task 2 already points at `--paper` -- now do what the deleted `header{}` rule did. `z-index:20` is close enough to Bootstrap's own `--bs-navbar-* ` stacking to not need restating; nothing else on the page uses a `z-index` between the old sheet's `29`/`30` and this, so there's no ordering regression to check for.)

Find:

```python
/* Four tabs plus the pill overflow 360px. Scroll rather than wrap -- a wrapped
   nav pushes the list down the fold on the smallest phone. */
nav{display:flex;align-items:center;gap:1.5rem;padding-bottom:.2rem;
  overflow-x:auto;scrollbar-width:none}
nav::-webkit-scrollbar{display:none}
nav a{padding:.65rem 0 .75rem;font-size:1rem;color:var(--soft);
  white-space:nowrap;border-bottom:2px solid transparent;transition:color .15s,border-color .15s}
nav a.on{color:var(--ink);border-bottom-color:var(--accent)}
```

Replace with:

```python
/* Four tabs plus the pill overflow 360px. Scroll rather than wrap -- a wrapped
   nav pushes the list down the fold on the smallest phone. */
#nav{gap:1.5rem;padding-bottom:.2rem;overflow-x:auto;scrollbar-width:none}
#nav::-webkit-scrollbar{display:none}
#nav a{padding:.65rem 0 .75rem;font-size:1rem;color:var(--soft);
  white-space:nowrap;border-bottom:2px solid transparent;transition:color .15s,border-color .15s}
#nav a.on{color:var(--ink);border-bottom-color:var(--accent)}
```

(Selectors narrow from the bare `nav` tag to `#nav`, since the outer element is now `<nav class="navbar">` too and would otherwise pick up rules meant for the tab strip.)

Find:

```python
/* Plan is a toggle, not a section -- a pill on the right, so it does not read
   as a fourth heading in a row of three. */
nav a#plantoggle{margin-left:auto;padding:.45rem 1.1rem;border:1px solid var(--rule);
  border-radius:999px;background:var(--card);font-size:.9rem;
  margin-bottom:.3rem;cursor:pointer}
nav a#plantoggle:hover{border-color:var(--accent);color:var(--accent)}
nav a#plantoggle.on{background:var(--accent);border-color:var(--accent);color:var(--on-accent)}
```

Replace with:

```python
/* Plan is a toggle, not a section -- a pill on the right, so it does not read
   as a fourth heading in a row of three. */
#nav a#plantoggle{margin-left:auto;padding:.45rem 1.1rem;border:1px solid var(--rule);
  border-radius:999px;background:var(--card);font-size:.9rem;
  margin-bottom:.3rem;cursor:pointer}
#nav a#plantoggle:hover{border-color:var(--accent);color:var(--accent)}
#nav a#plantoggle.on{background:var(--accent);border-color:var(--accent);color:var(--on-accent)}
```

- [ ] **Step 3: Restyle the theme toggle button**

The `#theme` button already gets `class="btn btn-sm rounded-circle"` from Step 1. Its existing CSS rule sizes and centers the icon; Bootstrap's `.btn` adds a background/border that would compete with the existing circular treatment, so trim the existing rule down to what it still needs:

Find:

```python
/* Theme is a page-level setting, so it sits in the brand row rather than
   competing with four section tabs for 360px of nav. */
#theme{margin-left:auto;align-self:center;display:flex;align-items:center;
  justify-content:center;width:2.5rem;height:2.5rem;padding:0;
  border-radius:999px;color:var(--soft)}
```

Replace with:

```python
/* Theme is a page-level setting, so it sits in the brand row rather than
   competing with four section tabs for 360px of nav. .btn already gives it a
   border and hover state -- this rule only fixes the circle's size and
   centers the icon inside it. */
#theme{margin-left:auto;align-self:center;display:flex;align-items:center;
  justify-content:center;width:2.5rem;height:2.5rem;padding:0;color:var(--soft)}
```

- [ ] **Step 4: Regenerate and run the full suite**

```bash
.venv/bin/python bin/browse.py
.venv/bin/python tests/test_browse.py
```
Expected: `Ran 60 tests ... OK`.

- [ ] **Step 5: Manual check**

Open the page at phone width (~375px) and confirm: the five nav items (Today/Recipes/Plans/Orders/Plan) still sit on one row without wrapping or a hamburger appearing, the brand text and theme toggle still sit correctly, and the nav is still sticky when scrolling the recipe list. Toggle dark mode and confirm the navbar's background and text follow the theme.

- [ ] **Step 6: Commit**

```bash
git add bin/browse.py index.html
git commit -m "Nav -> Bootstrap navbar (.navbar-expand, no toggler needed)

Same five tabs, same hash routing, same plantoggle pill -- only the
scaffolding classes change. .navbar-expand (no breakpoint suffix)
keeps the tabs in one row at every width, matching the existing
scroll-rather-than-wrap behavior without a hamburger."
```

---

### Task 4: Filter UI → Offcanvas, form controls, chips

**Files:**
- Modify: `bin/browse.py` (`facetPanel()`, `quickbar()`, `recipeList()`'s tools row, `wireFilters()`, the `.sheet`/`.scrim`/`.chip`/`.quickbar`/input/button/badge CSS, the `<div class="scrim">` in the static HTML shell)

**Interfaces:**
- Consumes: `bootstrap.Offcanvas` (from Task 1), `--bs-*` variables (from Task 2).
- Produces: `facetPanel()` now returns an `<div class="offcanvas ...">` instead of `<div class="sheet">`; there is no more `#scrim` element or `sheet.hidden`/`scrim.hidden` toggling anywhere in the file. `wireFilters()`'s external behavior (which facets are active, how the hash reflects them) is unchanged — only how the panel opens and closes changes.

This is the biggest single task in the plan because the filter sheet, its trigger button, and its two callers (`recipeList()`'s tools row and `wireFilters()`'s event wiring) all change together — splitting it further would leave an intermediate commit where the sheet markup and its JS don't agree.

- [ ] **Step 1: Turn `facetPanel()`'s sheet into an Offcanvas**

In `bin/browse.py`, find:

```python
function facetPanel(){
  const rows = FACETS.map(k => `<div class="facet" data-facet="${k}"><h3>${k}</h3><div class="chips">` +
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
```

Replace with:

```python
function facetPanel(){
  const rows = FACETS.map(k => `<div class="facet" data-facet="${k}"><h3>${k}</h3><div class="chips">` +
    D.facets[k].map(v => {
      const on = (route.f[k]||[]).includes(v);
      return `<button class="chip ${on?'on':''}" data-facet="${k}" data-value="${v}">${nice(v)}</button>`;
    }).join('') + `</div></div>`).join('');
  return `<div class="offcanvas offcanvas-bottom offcanvas-lg" tabindex="-1" id="sheet">
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
```

(`.btn-close` is Bootstrap's standard dismiss icon — it replaces the old text "Done" button at the top, matching how Offcanvas is conventionally closed. `#done`'s id is kept on the close button so `wireFilters()`'s existing `document.getElementById('done')` lookup keeps working. `.offcanvas-lg` is the class that makes it a sliding bottom overlay below 992px and a static inline block at 992px and up — see the plan's Global Constraints on the breakpoint move.)

- [ ] **Step 2: Restyle the quickbar's and facet panel's chip buttons onto the new variables**

Find:

```python
function quickbar(){
  const on = v => (route.f.slot||[]).includes(v);
  return `<div class="quickbar">${D.facets.slot.map(v =>
    `<button class="chip ${on(v)?'on':''}" data-facet="slot" data-value="${v}">${nice(v)}</button>`
  ).join('')}</div>`;
}
```

This function is unchanged — it already emits `.chip` buttons, and `.chip` is staying a custom class (see the spec's component mapping: no Bootstrap primitive fits multi-select toggle pills). Its CSS already reads `--paper`/`--rule`/`--accent`/`--accent-soft`, which Task 2 didn't touch, so no edit is needed here. Move on to the tools row.

- [ ] **Step 3: Restyle the tools row's search input, sort select, and filter trigger**

In `bin/browse.py`, find:

```python
  const n = activeCount();
  return `<p class="lede">${D.recipes.length} Recipes. Showing ${hits.length}.</p>
    <div class="tools">
      <input type="search" id="q" placeholder="Search recipes"
             title="Searches titles, ingredients, Pinned products and method"
             value="${esc(route.q)}">
      <select id="sort" aria-label="Sort within each Slot">${
        Object.entries(SORTS).map(([k,v]) =>
          `<option value="${k}"${k === route.sort ? ' selected' : ''}>${v.label}</option>`
        ).join('')}</select>
      <button id="filterbtn">Filters${n ? `<span class="badge">${n}</span>` : ''}</button>
    </div>
    ${quickbar()}
    <div class="layout">${facetPanel()}<div>${body}</div></div>`;
```

Replace with:

```python
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
```

(`data-bs-toggle`/`data-bs-target` are Bootstrap's own declarative wiring — clicking `#filterbtn` now opens the offcanvas without any JS on our side. `wireFilters()` still attaches a JS handler below for the cases Bootstrap's declarative API doesn't cover: closing after a chip click while the panel is open on narrow screens, and the "Clear all" button.)

- [ ] **Step 4: Rewrite `wireFilters()` to drive the Offcanvas instance instead of the hidden-attribute/scrim toggle**

Find the whole function:

```python
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

  document.querySelectorAll('.chip').forEach(chip => chip.onclick = () => {
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
```

Replace with:

```python
function wireFilters(){
  const sheet = document.getElementById('sheet');
  const wide = () => matchMedia('(min-width:992px)').matches;
  /* getOrCreateInstance, not `new` -- recipeList() rebuilds #sheet's markup
     from scratch on every render(), so any instance tied to the previous
     node is already gone with it. Bootstrap tracks the instance on the DOM
     node itself, so asking for "the instance for this node, creating one if
     there isn't one yet" is always correct, whether this is the first
     render or the fiftieth. */
  const offcanvas = () => bootstrap.Offcanvas.getOrCreateInstance(sheet);
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
```

(The old code re-showed the sheet+scrim after a re-render by setting `hidden = false` directly, bypassing whatever "open" meant. The Offcanvas equivalent is calling `.show()` on the fresh instance, which also redraws the backdrop Bootstrap owns. `#filterbtn`'s own open action no longer needs a JS handler at all — that's the `data-bs-toggle` attribute from Step 3.)

- [ ] **Step 5: Remove the now-unused `#scrim` element and its CSS**

In `bin/browse.py`, find:

```python
<main class="wrap"><div id="app"></div></main>
<div class="scrim" id="scrim" hidden></div>
<div class="drawer" id="drawer" hidden></div>
```

Replace with:

```python
<main class="wrap"><div id="app"></div></main>
<div class="drawer" id="drawer" hidden></div>
```

Find:

```python
.sheet{position:fixed;inset:auto 0 0 0;z-index:30;background:var(--card);
  border-top:1px solid var(--rule);max-height:78vh;overflow:auto;padding:1.3rem;
  box-shadow:0 -8px 30px var(--shade)}
.sheet[hidden]{display:none}
.scrim{position:fixed;inset:0;z-index:29;background:var(--scrim)}
.scrim[hidden]{display:none}
.facet{margin-bottom:1.3rem}
```

Replace with:

```python
.facet{margin-bottom:1.3rem}
```

(Offcanvas provides its own fixed positioning, max-height, backdrop, and box-shadow via its own CSS classes; the hand-rolled `.sheet`/`.scrim` rules would otherwise sit dead in the stylesheet. The `sheet-foot` rule is kept below since the "Clear all" button still uses it for its top border/spacing.)

- [ ] **Step 6: Move the wide-screen sheet override to 992px, and keep its sticky behavior**

Find (inside the `@media(min-width:56rem)` block from Task 3's not-yet-renamed selectors — this step renames the whole block, so do it once, here):

```python
@media(min-width:56rem){
  body{font-size:17.5px}
  .layout{display:grid;grid-template-columns:15rem 1fr;gap:2.5rem;align-items:start}
  .sheet{position:sticky;top:6.4rem;inset:auto;max-height:none;overflow:visible;
    box-shadow:none;border:1px solid var(--rule);border-radius:var(--radius);padding:1.1rem}
  .sheet[hidden]{display:block}
  .scrim{display:none!important}
  .sheet-foot .close{display:none}
  #filterbtn{display:none}
  .quickbar{display:none}
  .facet[data-facet="slot"]{display:block}
  .day dl{grid-template-columns:6.5rem 1fr}
  ul.list a .t{flex:1 1 auto}
  ul.list a .macro{margin-left:auto}
  ul.list a .meta{flex:1 0 100%}
}
```

Replace with:

```python
@media(min-width:992px){
  body{font-size:17.5px}
  .layout{display:grid;grid-template-columns:15rem 1fr;gap:2.5rem;align-items:start}
  /* .offcanvas-lg already goes static and undecorated at this width -- this
     adds back the one thing it doesn't do on its own: staying in view while
     the list scrolls past it. */
  #sheet{position:sticky;top:6.4rem;border:1px solid var(--rule);
    border-radius:var(--radius);padding:1.1rem}
  #filterbtn{display:none}
  .quickbar{display:none}
  .facet[data-facet="slot"]{display:block}
  .day dl{grid-template-columns:6.5rem 1fr}
  ul.list a .t{flex:1 1 auto}
  ul.list a .macro{margin-left:auto}
  ul.list a .meta{flex:1 0 100%}
}
```

(`.sheet-foot .close` and its rule are dropped -- the "Done" button no longer exists as a text button to hide at wide widths; it's the `.btn-close` icon inside `.offcanvas-header`, and `.offcanvas-lg` already hides the whole header at 992px and up via Bootstrap's own CSS, confirmed by reading the downloaded stylesheet.)

- [ ] **Step 7: Regenerate and run the full suite**

```bash
.venv/bin/python bin/browse.py
.venv/bin/python tests/test_browse.py
```
Expected: `Ran 60 tests ... OK`.

- [ ] **Step 8: Manual check, at both widths**

At phone width (~375px): tap "Filters" — the panel slides up from the bottom with a backdrop; tap a chip inside it — the panel stays open and the count updates; tap the `×` close icon — it slides away. Tap a Slot pill in the always-visible quickbar — the list filters without opening anything.

At desktop width (≥992px): the filter panel sits as a sidebar to the left of the list, no backdrop, no "Filters" button visible, and it stays in view while scrolling the list.

Resize the window across 992px with the panel open on the narrow side first, to confirm nothing gets stuck half-open.

- [ ] **Step 9: Commit**

```bash
git add bin/browse.py index.html
git commit -m "Filter sheet -> Bootstrap Offcanvas

.offcanvas-bottom.offcanvas-lg replaces the hand-rolled hidden-
attribute/scrim toggle -- Bootstrap owns the backdrop, the slide
animation, and (at 992px and up) turning the panel into a static
inline block, which this keeps sticky with three lines of CSS.
Search/sort/filter-trigger become form-control/form-select/btn;
chips are unchanged, no Bootstrap primitive fits a multi-select
toggle pill."
```

---

### Task 5: Recipe list rows → `list-group`

**Files:**
- Modify: `bin/browse.py` (`recipeList()`'s row markup, `.group`/`ul.list`/`.macro`/`.meta`/`.dot`/`.empty` CSS)

**Interfaces:**
- Consumes: `--bs-body-bg`, `--bs-border-color`, `--bs-tertiary-bg`, `--bs-primary` (from Task 2).
- Produces: no change to what data each row shows or how it links — only the wrapping element changes from `<ul class="list"><li><a>` to `<div class="list-group"><a class="list-group-item list-group-item-action">`.

- [ ] **Step 1: Change the row markup**

In `bin/browse.py`, find:

```python
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
```

Replace with:

```python
  const body = groups.length ? groups.map(([slot, rs]) => `
    <div class="group"><h2>${slot}</h2><em>${rs.length}</em></div>
    <div class="list-group list-group-flush">${rs.map(r => `<a class="list-group-item list-group-item-action"
      href="#recipe/${r.slug}${qs()}">
      <span class="t">${esc(r.title)}</span>
      <span class="macro">${scoreDot('protein',r)}${g(r.protein_g)} · ${kc(r.kcal)} kcal</span>
      <span class="meta">${[star(r.rating), nice(r.protein), r.effort ? r.effort+' effort' : '',
        (r.appliances||[]).map(nice).join(', ') || 'no appliance',
        (r.tags||[]).map(nice).join(', ')].filter(Boolean).join(' · ')}</span>
    </a>`).join('')}</div>`).join('')
    : `<p class="empty">No Recipe matches those filters.</p>`;
```

(`list-group-flush` drops Bootstrap's default outer border/rounded corners, matching how the rows currently sit flush against the page rather than in a boxed card. `wirePlanClicks()`, in Plan mode, delegates from `#app` and reads `event.target.closest('a')` -- unaffected by the wrapper tag changing from `<ul><li>` to `<div>`, since it was never selecting on `<li>` to begin with; verify this in Step 4.)

- [ ] **Step 2: Replace the list/group CSS with the Bootstrap-aware equivalents**

Find:

```python
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
```

Replace with:

```python
.group{margin:2.4rem 0 .8rem;display:flex;align-items:baseline;gap:.6rem;
  border-bottom:1px solid var(--rule);padding-bottom:.5rem}
.group h2{font-size:1.05rem;font-weight:600;color:var(--accent)}
.group em{font-style:normal;font-size:.85rem;color:var(--soft)}
/* list-group-flush already gives every row its bottom border and strips the
   outer box; this only adds back the row's internal flex layout, since a
   title/macro/meta row isn't something Bootstrap's list-group has an
   opinion about. On a phone the title takes the whole width and the macro
   drops onto the meta line -- squeezing it into a right column wrapped
   nearly every title onto two lines. Wide enough, and the macro returns to
   its right-aligned column where a sorted list can be scanned. */
.list-group-item{display:flex;flex-wrap:wrap;align-items:baseline;gap:.2rem .6rem;
  padding:.9rem .3rem;background:transparent}
.list-group-item .t{flex:1 0 100%;font-size:1.05rem;font-weight:500;color:var(--ink)}
.list-group-item .macro{order:2}
.list-group-item .meta{order:3;flex:1;margin-top:0}
```

(Bootstrap's `.list-group-item-action:hover` already applies `--bs-tertiary-bg` as the hover background -- which Task 2 points at `--card` -- so the old `ul.list a:hover{background:var(--card)}` rule is simply not needed any more rather than being translated.)

Find the wide-screen media query rules from Task 4's Step 6 (now at `@media(min-width:992px)`):

```python
  ul.list a .t{flex:1 1 auto}
  ul.list a .macro{margin-left:auto}
  ul.list a .meta{flex:1 0 100%}
```

Replace with:

```python
  .list-group-item .t{flex:1 1 auto}
  .list-group-item .macro{margin-left:auto}
  .list-group-item .meta{flex:1 0 100%}
```

- [ ] **Step 3: `.empty`, `.macro`, `.meta`, `.dot` are unchanged**

These are shared with other views (recipe detail, plan detail) and already read `--soft`/`--ink`/`--in`/`--under`/`--over`, which Task 2 didn't touch. No edit needed — confirmed by re-reading their definitions, which don't reference `ul.list` or `.list-group` in their selectors.

- [ ] **Step 4: Confirm Plan mode's click delegation still works**

Read `wirePlanClicks()` in `bin/browse.py` (find `function wirePlanClicks(){`). Confirm its click handler resolves the clicked Recipe via `event.target.closest('a[href^="#recipe/"]')` or equivalent — not via `li` or `ul.list` — so the tag change from Step 1 doesn't affect it. (If it turns out to reference `li` anywhere, that's a real finding: stop and fix it here rather than in a later task, since this is the task that changed the tag it would be matching against.)

- [ ] **Step 5: Regenerate and run the full suite**

```bash
.venv/bin/python bin/browse.py
.venv/bin/python tests/test_browse.py
```
Expected: `Ran 60 tests ... OK`.

- [ ] **Step 6: Manual check**

Open the Recipes list. Confirm rows still show title/macro/meta in the same layout at both phone and desktop width, hovering a row still highlights it, and clicking a row still opens the Recipe. Turn on Plan mode and confirm clicking a row still fills the current Slot instead of navigating.

- [ ] **Step 7: Commit**

```bash
git add bin/browse.py index.html
git commit -m "Recipe list rows -> Bootstrap list-group

<ul class=list><li><a> becomes <div class=list-group-flush><a
class=list-group-item-action> -- Bootstrap owns the row borders and
hover background (via --bs-tertiary-bg, already the page's --card);
the title/macro/meta flex layout inside each row is unchanged."
```

---

### Task 6: Plan-mode wizard bar → `fixed-bottom` utilities

**Files:**
- Modify: `bin/browse.py` (`renderDrawer()`'s markup, the `.drawer` CSS)

**Interfaces:**
- Consumes: `--bs-tertiary-bg`, `--bs-border-color` (from Task 2).
- Produces: no change to `renderDrawer()`'s state logic (`planDone()`, `PLAN_SEQ`, `cursor`, the four button handlers) — only the classes on the container and its buttons change. `body.plan-on{padding-bottom:...}` is unchanged, since it's sized for the drawer regardless of which classes render it.

- [ ] **Step 1: Give the drawer container Bootstrap's fixed-bottom utilities**

In `bin/browse.py`, find:

```python
<div class="drawer" id="drawer" hidden></div>
```

Replace with:

```python
<div class="drawer fixed-bottom border-top shadow" id="drawer" hidden></div>
```

- [ ] **Step 2: Drop the hand-rolled positioning from `.drawer`'s CSS, keep its layout rules**

Find:

```python
/* Plan mode. The drawer is its own thing, not a reused .sheet -- .sheet turns
   into a sticky sidebar on wide screens and this must stay at the bottom. */
.drawer{position:fixed;inset:auto 0 0 0;z-index:40;background:var(--card);
  border-top:1px solid var(--rule);box-shadow:0 -2px 14px var(--shade);
  padding:.85rem 0}
.drawer .wrap{display:flex;align-items:center;gap:.7rem;flex-wrap:wrap}
```

Replace with:

```python
/* Plan mode. The drawer is its own thing, not a reused .sheet -- .sheet turns
   into a sticky sidebar on wide screens and this must stay at the bottom.
   .fixed-bottom/.border-top/.shadow (on the element itself, in the HTML)
   now do the positioning and chrome this rule used to; --bs-tertiary-bg and
   --bs-border-color, from Task 2, keep the colors the same as before. */
.drawer{background:var(--bs-tertiary-bg);padding:.85rem 0}
.drawer .wrap{display:flex;align-items:center;gap:.7rem;flex-wrap:wrap}
```

- [ ] **Step 3: Restyle the drawer's own buttons**

In `bin/browse.py`, find:

```python
  drawer.innerHTML = `<div class="wrap">
    <span class="where">${here}</span>
    <span class="macro">${done} / ${PLAN_SEQ.length}</span>
    <span class="rest">
      <button id="planback"${cursor ? '' : ' disabled'}>← Back</button>
      ${at ? `<button id="planskip">Skip</button>` : ''}
      <button id="planout"${done < PLAN_SEQ.length ? ' disabled' : ''}>Checkout</button>
      <button id="planexit">Exit</button>
    </span></div>`;
```

Replace with:

```python
  drawer.innerHTML = `<div class="wrap">
    <span class="where">${here}</span>
    <span class="macro">${done} / ${PLAN_SEQ.length}</span>
    <span class="rest">
      <button id="planback" class="btn btn-outline-secondary btn-sm"${cursor ? '' : ' disabled'}>← Back</button>
      ${at ? `<button id="planskip" class="btn btn-outline-secondary btn-sm">Skip</button>` : ''}
      <button id="planout" class="btn btn-outline-primary btn-sm"${done < PLAN_SEQ.length ? ' disabled' : ''}>Checkout</button>
      <button id="planexit" class="btn btn-outline-secondary btn-sm">Exit</button>
    </span></div>`;
```

(`disabled` is a plain HTML attribute here, same as before — Bootstrap's `.btn` CSS already styles `:disabled` via its own rule, so the page's existing `button[disabled]{opacity:.45;cursor:not-allowed}` rule, further down the stylesheet, now doubles up with Bootstrap's own disabled treatment. Leave that rule as-is: it also still applies to any out-of-scope button elsewhere on the page — e.g. `checkoutView()`'s `#edit`/`#startover` — that never gained a `.btn` class in this plan.)

- [ ] **Step 4: Regenerate and run the full suite**

```bash
.venv/bin/python bin/browse.py
.venv/bin/python tests/test_browse.py
```
Expected: `Ran 60 tests ... OK`.

- [ ] **Step 5: Manual check**

Turn on Plan mode. Confirm the wizard bar sits fixed to the bottom of the viewport, the list still scrolls underneath it without the last row hiding behind it, and Back/Skip/Checkout/Exit all still work (Back is disabled on the first Slot, Checkout is disabled until all 28 are filled). Toggle dark mode while in Plan mode and confirm the bar's background follows.

- [ ] **Step 6: Commit**

```bash
git add bin/browse.py index.html
git commit -m "Plan-mode wizard bar -> Bootstrap fixed-bottom utilities

No JS component needed -- .fixed-bottom/.border-top/.shadow replace
the hand-rolled position:fixed/box-shadow rule, and the four wizard
buttons get .btn styling. renderDrawer()'s own state logic (cursor,
planDone(), the four click handlers) is untouched."
```

---

### Task 7: Final regeneration, full verification, and ticket bookkeeping

**Files:**
- Modify: `.scratch/meal-planning-system/issues/24-browse-the-pool.md` (status note)

**Interfaces:** None — this task produces no new interface, it closes out the branch's work.

- [ ] **Step 1: Full regeneration and test run, from a clean check**

```bash
.venv/bin/python bin/browse.py
.venv/bin/python bin/browse.py --check
.venv/bin/python tests/test_browse.py
```
Expected: `--check` reports the committed page is current (this only holds if Step 2's `git add`/commit below includes `index.html`); the suite reports `Ran 60 tests ... OK`.

- [ ] **Step 2: Full manual pass, both themes, both widths**

Walk the whole page, not just the pieces each task already checked in isolation:
- Today, Recipes, Plans, Orders, and Plan mode (start to checkout) all still work.
- Toggle dark/light at least once on each of those views.
- Resize across 992px at least once on the Recipes view with the filter panel open.
- Confirm the Slot quickbar (added before this branch existed) still sits under the search bar on narrow screens and still hides at 992px and up, since Task 4 touched the same media query block it depends on.

- [ ] **Step 3: Record the re-skin in ticket 24**

In `.scratch/meal-planning-system/issues/24-browse-the-pool.md`, find the amendment this branch already added (from the ticket-amendment commit that preceded this plan):

```markdown
  **Amended on 20 September 2026**: "no runtime fetch" is narrowed to "no
  fetch of the page's own data." The user asked for a more out-of-the-box
  mobile UI than hand-rolled CSS was giving the sheet/drawer/chip components,
  and chose Bootstrap 5 loaded from a CDN over vendoring it or staying
  vanilla. That is a runtime fetch — the page now needs network access to
  render and behave correctly, and degrades on `file://` or offline. The part
  of the original concern that survives: the page's own data is still fully
  inlined JSON, never fetched, so `bin/browse.py`'s output remains a single
  generated artifact with no build tool and no server-side pipeline.
```

Add a sentence directly after it recording that the re-skin this amendment was made for actually landed, so a future reader doesn't have to check branch history to know whether the amendment describes a plan or a fact:

```markdown
  **Carried out the same day**: the filter sheet, nav, recipe list, and
  Plan-mode wizard bar all now render as Bootstrap 5.3.8 components
  (Offcanvas, navbar, list-group, and utility classes respectively),
  restyled onto this page's own palette rather than Bootstrap's defaults.
  See `docs/superpowers/specs/2026-09-20-bootstrap-reskin-design.md` and
  `docs/superpowers/plans/2026-09-21-bootstrap-reskin.md`.
```

- [ ] **Step 4: Commit**

```bash
git add .scratch/meal-planning-system/issues/24-browse-the-pool.md
git commit -m "Record the Bootstrap re-skin's completion in ticket 24"
```

- [ ] **Step 5: Push the branch**

```bash
git push -u origin bootstrap-reskin
```

This branch is an experiment per the spec — pushing it makes it reviewable and backed up, but merging to `main` (and therefore to the live GitHub Pages site) is a separate decision for afterward, not part of this plan.

## Self-Review

**Spec coverage:**
- "Loading" section → Task 1.
- "Theming mechanics" section → Task 2.
- Component mapping table's 8 rows → Tasks 3 (nav), 4 (sheet/scrim, chips, select/range, search input, buttons in the tools row, badge), 5 (recipe list), 6 (drawer + its buttons).
- "Testing & verification" section → each task's regenerate/test/manual-check steps, plus Task 7's full pass.
- "Non-goals" (no change to what `bin/browse.py` parses/computes/redacts, no router changes, no offline fallback) — no task touches `build_payload`, `matches()`, `sorted()`, `readHash()`/`writeHash()`, or any Python-side parsing; confirmed by re-reading which functions each task's steps touch.

**Placeholder scan:** every step has literal find/replace code, not a description of what to change. The one deliberately open item from the spec (`--bs-*-rgb` values) is resolved with real computed numbers in Task 2, not deferred further.

**Type/name consistency:** `setTheme()` (Task 2) is the only new function introduced, used at its two call sites in the same task. `wireFilters()`'s `offcanvas()`/`isShown()`/`wide()` helpers (Task 4) are local to that function and don't need to match anything elsewhere. Every `id=` referenced by a `document.getElementById()` call in a later step (`sheet`, `done`, `filterbtn`, `q`, `sort`, `min`, `clear`, `drawer`, `planback`, `planskip`, `planout`, `planexit`) is defined in that same task's markup change, and no task renames an id another task's JS still looks up.

**Scope check:** seven tasks, each independently testable and committed, matches the spec's single-branch scope. No task depends on a later one's code — each leaves the page fully working before the next starts.

the title/macro/meta flex layout inside each row is unchanged."