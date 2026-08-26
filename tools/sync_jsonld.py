#!/usr/bin/env python3
"""Write the JSON-LD block into every calculator page.

    python3 tools/sync_jsonld.py           # rewrite the block in every calculator page
    python3 tools/sync_jsonld.py --check   # exit 1 if any page has drifted

Each page in calculators/ gets one <script type="application/ld+json"> between
`<!-- jsonld:start -->` and `<!-- jsonld:end -->` in its <head>. The block holds
two items:

  WebApplication  name, url, description and category, read from the page's
                  <h1>, canonical, meta description and breadcrumb.
  FAQPage         one Question per `.faq-item` on the page, with the answer
                  text of its `.faq-a`.

Nothing here is computed by the browser. The tool reads the page and writes
static HTML, the same as tools/sync_nav.py. Do not hand-edit the region: edit
the page's FAQ items or its <head> tags, then run the tool.

A page with no marker pair gets one on the first run. If the page carries a
hand-written ld+json script in its <head>, the markers replace that script.
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CALC_DIR = ROOT / "calculators"

SITE = "https://calculatoreuphoria.com"
PUBLISHER = {"@type": "Organization", "name": "Calculator Euphoria", "url": SITE + "/"}

# The breadcrumb category -> schema.org applicationCategory.
CATEGORY = {
    "Finance": "FinanceApplication",
    "Health": "HealthApplication",
    "Math": "UtilitiesApplication",
    "Everyday": "UtilitiesApplication",
}

START = "<!-- jsonld:start -->"
END = "<!-- jsonld:end -->"

TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")


def text_of(fragment):
    """Strip tags and entities from an HTML fragment and collapse whitespace."""
    return WS.sub(" ", html.unescape(TAG.sub("", fragment))).strip()


def first(pattern, text, flags=re.S):
    m = re.search(pattern, text, flags)
    return m.group(1) if m else None


def page_data(text, path):
    name = first(r"<h1[^>]*>(.*?)</h1>", text)
    canonical = first(r'<link rel="canonical" href="([^"]+)"', text)
    description = first(r'<meta name="description" content="([^"]*)"', text)
    crumb = first(r'<div class="breadcrumb">.*?<a href="/index\.html#[a-z]+">([^<]+)</a>', text)
    missing = [k for k, v in (("h1", name), ("canonical", canonical),
                              ("description", description)) if not v]
    if missing:
        raise SystemExit("%s: missing %s" % (path, ", ".join(missing)))

    faqs = []
    for item in re.findall(r'<div class="faq-item">(.*?)</div>\s*</div>', text, re.S):
        q = first(r'<button class="faq-q">(.*?)</button>', item)
        a = first(r'<div class="faq-a">(.*?)$', item)
        if q is None or a is None:
            continue
        faqs.append((text_of(q), text_of(a)))

    return {
        "name": text_of(name),
        "url": canonical,
        "description": html.unescape(description),
        "category": CATEGORY.get(crumb, "UtilitiesApplication"),
        "faqs": faqs,
    }


def render(data):
    app = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": data["name"],
        "url": data["url"],
        "description": data["description"],
        "applicationCategory": data["category"],
        "operatingSystem": "Any",
        "browserRequirements": "Requires JavaScript",
        "isAccessibleForFree": True,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "publisher": PUBLISHER,
    }
    items = [app]
    if data["faqs"]:
        items.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in data["faqs"]
            ],
        })
    body = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    # "</" inside a script element would end it early.
    body = body.replace("</", "<\\/")
    return '%s\n<script type="application/ld+json">\n%s\n</script>\n%s' % (START, body, END)


LEGACY = re.compile(r'<script type="application/ld\+json">.*?</script>\n?', re.S)
THEME = re.compile(r"(<script>try\{var t=localStorage\.getItem\('theme'\).*?</script>\n)")


def place_markers(text, path):
    """Return text with one marker pair in <head>, adding it when absent."""
    if START in text and END in text:
        return text
    head_end = text.index("</head>")
    head, rest = text[:head_end], text[head_end:]
    markers = START + END + "\n"
    if LEGACY.search(head):
        head = LEGACY.sub(markers, head, count=1)
    elif THEME.search(head):
        head = THEME.sub(lambda m: m.group(1) + markers, head, count=1)
    else:
        raise SystemExit("%s: no place for the jsonld markers" % path)
    return head + rest


REGION = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)


def sync(path):
    original = path.read_text(encoding="utf-8")
    text = place_markers(original, path)
    block = render(page_data(text, path))
    text = REGION.sub(lambda m: block, text, count=1)
    return original, text


def main():
    ap = argparse.ArgumentParser(description="Sync the JSON-LD block in every calculator page.")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any page's rendered block is stale")
    args = ap.parse_args()

    stale, written = [], []
    for path in sorted(CALC_DIR.glob("*.html")):
        original, text = sync(path)
        if text == original:
            continue
        if args.check:
            stale.append(path)
        else:
            path.write_text(text, encoding="utf-8")
            written.append(path)

    rel = lambda p: p.relative_to(ROOT)
    if args.check:
        if stale:
            print("stale JSON-LD in %d file(s):" % len(stale))
            for p in stale:
                print("  " + str(rel(p)))
            print("run: python3 tools/sync_jsonld.py")
            sys.exit(1)
        print("JSON-LD is up to date")
        return
    for p in written:
        print("wrote " + str(rel(p)))
    print("%d file(s) updated" % len(written))


if __name__ == "__main__":
    main()
