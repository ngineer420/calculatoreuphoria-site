# Calculator Euphoria

Source for [calculatoreuphoria.com](https://calculatoreuphoria.com) — a free collection of online calculators for math, finance, health and everyday life.

## Stack

Plain static HTML/CSS/JS. No build step, no framework, no server. Every calculator runs entirely client-side. Hosted on GitHub Pages with a custom domain (see `DEPLOY.md`).

## Structure

```
index.html                   Homepage: hero search, category filters, calculator grid
about.html, privacy-policy.html, terms.html
assets/style.css             Shared design system (light/dark theme via CSS variables)
assets/main.js                Shared behavior: theme toggle, mobile nav, FAQ accordions, hero search
calculators/*.html            One self-contained page per calculator (markup + inline logic)
CNAME                          GitHub Pages custom domain
robots.txt, sitemap.xml
```

## Adding a new calculator

1. Copy the closest existing page in `calculators/` as a starting point for the header/footer chrome and `.calc-app` / `.result-panel` layout classes already defined in `assets/style.css`.
2. Write the calculator's logic in an inline `<script>` at the bottom of the page — keep it dependency-free.
3. Add a card to the grid in `index.html` and an entry to the `CALCULATORS` array in `assets/main.js` (powers the hero search).
4. Add the new URL to `sitemap.xml`.

## Design system

Color, spacing, and component classes (`.calc-app`, `.field`, `.input-group`, `.result-panel`, `.toggle-group`, `.faq-item`, etc.) live in `assets/style.css`. Dark mode is automatic (`prefers-color-scheme`) with a manual override stored in `localStorage`.

## Privacy

Every calculator computes entirely in the browser. No calculator input is ever sent to a server.
