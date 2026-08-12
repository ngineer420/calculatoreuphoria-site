"""calculatoreuphoria.com navigation data — the single source of truth for the toolbar.

This is the ONLY file that differs between sites. `sync_nav.py` is generic and
copies verbatim. Nothing here is computed at runtime by the browser: sync_nav
renders it into the static HTML of every page.

Tier rule (portfolio spec, ngineer420.github.io#13): a page is tier 1 only if it
answers a *different question*. Every one of these 18 calculators does — there is
no preset family on this site, so there is no tier 2, no hub row and no in-panel
sibling chips.

hrefs carry the `.html` extension because that is what this site's canonicals,
sitemap, homepage cards and footer already use; the old `.calc-menu` was the one
place writing extensionless paths, which split every calculator's equity across
two URLs.
"""

# Noun used in the menu trigger: "All 18 calculators".
NOUN = "calculators"

# Tier-1 tools. The first eight are the rail, in traffic order; the rest are
# sheet-only. Order within a group is the sheet order.
#   label -> rail chip text, <= 18 chars
#   long  -> anchor text in the sheet
#   group -> sheet grouping key
TOOLS = [
    # --- the rail (first eight) ---
    {"href": "/calculators/mortgage-calculator.html",          "label": "Mortgage",       "long": "Mortgage Calculator",          "group": "finance",  "tier": 1},
    {"href": "/calculators/percentage-calculator.html",        "label": "Percentage",     "long": "Percentage Calculator",        "group": "math",     "tier": 1},
    {"href": "/calculators/loan-calculator.html",              "label": "Loan",           "long": "Loan Calculator",              "group": "finance",  "tier": 1},
    {"href": "/calculators/bmi-calculator.html",               "label": "BMI",            "long": "BMI Calculator",               "group": "health",   "tier": 1},
    {"href": "/calculators/tip-calculator.html",               "label": "Tip",            "long": "Tip Calculator",               "group": "finance",  "tier": 1},
    {"href": "/calculators/scientific-calculator.html",        "label": "Scientific",     "long": "Scientific Calculator",        "group": "math",     "tier": 1},
    {"href": "/calculators/age-calculator.html",               "label": "Age",            "long": "Age Calculator",               "group": "everyday", "tier": 1},
    {"href": "/calculators/unit-converter.html",               "label": "Unit Converter", "long": "Unit Converter",               "group": "everyday", "tier": 1},
    # --- sheet only ---
    {"href": "/calculators/compound-interest-calculator.html", "label": "Compound",       "long": "Compound Interest Calculator", "group": "finance",  "tier": 1},
    {"href": "/calculators/discount-calculator.html",          "label": "Discount",       "long": "Discount Calculator",          "group": "finance",  "tier": 1},
    {"href": "/calculators/sales-tax-calculator.html",         "label": "Sales Tax",      "long": "Sales Tax Calculator",         "group": "finance",  "tier": 1},
    {"href": "/calculators/simple-interest-calculator.html",   "label": "Simple Interest","long": "Simple Interest Calculator",   "group": "finance",  "tier": 1},
    {"href": "/calculators/calorie-calculator.html",           "label": "Calorie",        "long": "Calorie Calculator",           "group": "health",   "tier": 1},
    {"href": "/calculators/sleep-calculator.html",             "label": "Sleep",          "long": "Sleep Calculator",             "group": "health",   "tier": 1},
    {"href": "/calculators/gpa-calculator.html",               "label": "GPA",            "long": "GPA Calculator",               "group": "math",     "tier": 1},
    {"href": "/calculators/fraction-calculator.html",          "label": "Fraction",       "long": "Fraction Calculator",          "group": "math",     "tier": 1},
    {"href": "/calculators/date-calculator.html",              "label": "Date",           "long": "Date Calculator",              "group": "everyday", "tier": 1},
    {"href": "/calculators/aspect-ratio-calculator.html",      "label": "Aspect Ratio",   "long": "Aspect Ratio Calculator",      "group": "everyday", "tier": 1},
]

# Sheet groups, in order: (key, label, category hub). The site's own four
# categories, verbatim. The third element is the existing category anchor on the
# homepage grid, which is what absorbs the old header's Finance/Health/Math links
# with no destination lost — Home is now the brand, About lives in the footer.
GROUPS = [
    ("finance",  "Finance",  "/index.html#finance"),
    ("health",   "Health",   "/index.html#health"),
    ("math",     "Math",     "/index.html#math"),
    ("everyday", "Everyday", "/index.html#everyday"),
]

# No preset family on this site: every calculator answers a different question,
# so there is no tier-2 hub row and no in-panel sibling chips.
HUBS = []

# The homepage footer already carries a partial tool list and every page's footer
# carries the legal links; the rail plus the sheet carry all 18 calculators, so
# adding a footer duplicate would be boilerplate without a new crawl surface.
FOOTER = []

# One-time --migrate: what the legacy markup looked like and where the marker
# pair goes. Per-site, because the legacy markup is per-site. Ops run in order.
MIGRATE = [
    # The five-link header nav. Home is the brand and About moved to the footer;
    # Finance/Health/Math survive as the sheet's group labels.
    {"op": "strip", "pattern": r'\n    <nav>\n      <a href="/index\.html".*?\n    </nav>'},
    # The hamburger, which only ever opened those five links.
    {"op": "strip", "pattern": r'\n    <button class="icon-btn nav-toggle".*?\n    </button>'},
    # The second bar: 18 calculators in a scroller with no fade, no scrollbar and
    # no scroll-into-view, so 15 of 18 were unreachable at 390px.
    {"op": "strip", "pattern": r'\n<nav class="calc-menu".*?\n</nav>\n'},
    # The toolbar is a direct child of <body>, immediately after </header>.
    {"op": "insert_after", "region": "nav", "pattern": r"</header>", "indent": ""},
]
