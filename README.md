# Calculator Euphoria

Source for [calculatoreuphoria.com](https://calculatoreuphoria.com) — a free collection of online calculators for math, finance, health and everyday life.

## Stack

Plain static HTML/CSS/JS. No build step, no framework, no server. Every calculator runs entirely client-side. Hosted on GitHub Pages with a custom domain (see `DEPLOY.md`).

## Structure

```
index.html                   Homepage: hero search, category filters, calculator grid
about.html, privacy-policy.html, terms.html
assets/style.css             Shared design system (light/dark theme via CSS variables)
assets/main.js                Shared behavior: theme toggle, toolbar, FAQ accordions, hero search
calculators/*.html            One self-contained page per calculator (markup + inline logic)
tools/nav_data.py             The calculator list behind the toolbar — the only file to edit
tools/sync_nav.py             Writes the toolbar into every page (portfolio-wide, copied verbatim)
CNAME                          GitHub Pages custom domain
robots.txt, sitemap.xml
```

## Navigation

Every page carries one `<nav class="toolbar">` — a menu trigger plus a single non-wrapping
row of calculator chips — rendered between `<!-- nav:start -->` and `<!-- nav:end -->`.

**Do not hand-edit that region.** It is written into all 26 files from `tools/nav_data.py`:

```sh
python3 tools/sync_nav.py           # rewrite every marked region
python3 tools/sync_nav.py --check   # exit 1 if any page has drifted (run before deploy)
```

This is not a build step — it writes the same static HTML the repo already ships and
commits it, so hosting is unchanged.

## Adding a new calculator

1. Copy the closest existing page in `calculators/` as a starting point for the header/footer chrome and `.calc-app` / `.result-panel` layout classes already defined in `assets/style.css`.
2. Write the calculator's logic in an inline `<script>` at the bottom of the page — keep it dependency-free.
3. Add a card to the grid in `index.html` and an entry to the `CALCULATORS` array in `assets/main.js` (powers the hero search).
4. Add it to `TOOLS` in `tools/nav_data.py` and run `python3 tools/sync_nav.py`.
5. Add the new URL to `sitemap.xml`.

## Design system

Color, spacing, and component classes (`.calc-app`, `.field`, `.input-group`, `.result-panel`, `.toggle-group`, `.faq-item`, etc.) live in `assets/style.css`. Dark mode is automatic (`prefers-color-scheme`) with a manual override stored in `localStorage`.

## Privacy

Every calculator computes entirely in the browser. No calculator input is ever sent to a server.
