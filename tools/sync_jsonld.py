#!/usr/bin/env python3
"""Write the JSON-LD block and the Open Graph tags into every page below the root.

    python3 tools/sync_jsonld.py           # rewrite both regions in every page
    python3 tools/sync_jsonld.py --check   # exit 1 if any page has drifted

Every page below the site root gets two managed regions in its <head>:

  <!-- jsonld:start -->  one <script type="application/ld+json"> holding an
  <!-- jsonld:end -->    array of schema.org items.

  <!-- og:start -->      the Open Graph and Twitter tags that name the page.
  <!-- og:end -->        The og:image tags stay hand-written, because one
                         image serves the whole site.

The items in the JSON-LD array are:

  WebApplication  a calculator page. Name, url, description and category, read
                  from the page's <h1>, canonical, meta description and
                  breadcrumb.
  Article         a page in articles/. datePublished and dateModified come from
                  git, because the markup carries no date.
  WebPage         about, terms and privacy.
  BreadcrumbList  every page. A calculator reads its own visible breadcrumb.
                  Everything else gets Home plus its own title.
  FAQPage         one Question per `.faq-item` on the page, with the answer
                  text of its `.faq-a`. Emitted only where the markup exists.

Nothing here is computed by the browser. The tool reads the page and writes
static HTML, the same as tools/sync_nav.py. Do not hand-edit either region:
edit the page's FAQ items or its <head> tags, then run the tool.

A page with no marker pair gets one on the first run. If the page carries a
hand-written ld+json script in its <head>, the markers replace that script.
"""

import argparse
import html
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SITE = "https://calculatoreuphoria.com"
PUBLISHER = {"@type": "Organization", "name": "Calculator Euphoria", "url": SITE + "/"}
OG_IMAGE = SITE + "/assets/og-image.png"

# The root is its own hand-written case, and a 404 belongs in no index.
# privacy-policy.html is the redirect stub left behind by the rename.
SKIP = {"index.html", "404.html", "privacy-policy.html"}

# The breadcrumb category -> schema.org applicationCategory.
CATEGORY = {
    "Finance": "FinanceApplication",
    "Health": "HealthApplication",
    "Math": "UtilitiesApplication",
    "Everyday": "UtilitiesApplication",
}

START = "<!-- jsonld:start -->"
END = "<!-- jsonld:end -->"
OG_START = "<!-- og:start -->"
OG_END = "<!-- og:end -->"

TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")


def text_of(fragment):
    """Strip tags and entities from an HTML fragment and collapse whitespace."""
    return WS.sub(" ", html.unescape(TAG.sub("", fragment))).strip()


def first(pattern, text, flags=re.S):
    m = re.search(pattern, text, flags)
    return m.group(1) if m else None


# --------------------------------------------------------------------------
# Dates. The markup carries none, so git is the only honest source. A file with
# uncommitted work is newer than its last commit, so it falls back to mtime.
# --------------------------------------------------------------------------

def git(*args):
    try:
        out = subprocess.run(("git",) + args, cwd=str(ROOT), capture_output=True,
                             text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def mtime_date(path):
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")


def file_dates(path):
    """Return (created, modified) as YYYY-MM-DD."""
    rel = path.relative_to(ROOT).as_posix()
    dirty = bool(git("status", "--porcelain", "--", rel))
    log = git("log", "--follow", "--format=%cs", "--", rel)
    dates = [d for d in log.split("\n") if d]
    created = dates[-1] if dates else mtime_date(path)
    if dirty or not dates:
        modified = mtime_date(path)
    else:
        modified = dates[0]
    if modified < created:
        modified = created
    return created, modified


# --------------------------------------------------------------------------
# Reading a page
# --------------------------------------------------------------------------

def page_kind(path):
    rel = path.relative_to(ROOT)
    if rel.parts[0] == "calculators":
        return "calculator"
    if rel.parts[0] == "articles":
        return "article"
    return "page"


def page_data(text, path):
    name = first(r"<h1[^>]*>(.*?)</h1>", text)
    canonical = first(r'<link rel="canonical" href="([^"]+)"', text)
    description = first(r'<meta name="description" content="([^"]*)"', text)
    crumb = first(r'<div class="breadcrumb">.*?<a href="(/index\.html#[a-z]+)">([^<]+)</a>',
                  text)
    crumb_pair = re.search(
        r'<div class="breadcrumb">.*?<a href="(/index\.html#[a-z]+)">([^<]+)</a>', text, re.S)
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

    created, modified = file_dates(path)
    return {
        "kind": page_kind(path),
        "name": text_of(name),
        "url": canonical,
        "description": html.unescape(description),
        "crumb_href": crumb_pair.group(1) if crumb_pair else None,
        "crumb_label": text_of(crumb_pair.group(2)) if crumb_pair else None,
        "category": CATEGORY.get(text_of(crumb_pair.group(2)) if crumb_pair else "",
                                 "UtilitiesApplication"),
        "faqs": faqs,
        "created": created,
        "modified": modified,
    }


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def breadcrumb(data):
    """One BreadcrumbList. Home, then the category when the page shows one."""
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}]
    if data["crumb_href"] and data["crumb_label"]:
        items.append({"@type": "ListItem", "position": 2, "name": data["crumb_label"],
                      "item": SITE + data["crumb_href"]})
    # The last crumb is the page itself. It carries no `item`, because a link
    # to the page a reader is already on is not a step in the trail.
    items.append({"@type": "ListItem", "position": len(items) + 1, "name": data["name"]})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": items}


def primary(data):
    if data["kind"] == "calculator":
        return {
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
    if data["kind"] == "article":
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": data["name"],
            "url": data["url"],
            "description": data["description"],
            "image": OG_IMAGE,
            "datePublished": data["created"],
            "dateModified": data["modified"],
            "author": PUBLISHER,
            "publisher": PUBLISHER,
            "mainEntityOfPage": {"@type": "WebPage", "@id": data["url"]},
            "isAccessibleForFree": True,
        }
    return {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": data["name"],
        "url": data["url"],
        "description": data["description"],
        "dateModified": data["modified"],
        "publisher": PUBLISHER,
    }


def render_jsonld(data):
    items = [primary(data), breadcrumb(data)]
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


def esc_attr(value):
    return (value.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def render_og(data):
    og_type = "article" if data["kind"] == "article" else "website"
    tags = [
        ('property', "og:type", og_type),
        ('property', "og:site_name", "Calculator Euphoria"),
        ('property', "og:title", data["name"]),
        ('property', "og:description", data["description"]),
        ('property', "og:url", data["url"]),
        ('name', "twitter:title", data["name"]),
        ('name', "twitter:description", data["description"]),
    ]
    lines = ['<meta %s="%s" content="%s">' % (kind, key, esc_attr(value))
             for kind, key, value in tags]
    return "%s\n%s\n%s" % (OG_START, "\n".join(lines), OG_END)


# --------------------------------------------------------------------------
# Splicing
# --------------------------------------------------------------------------

LEGACY = re.compile(r'<script type="application/ld\+json">.*?</script>\n?', re.S)
THEME = re.compile(r"(<script>try\{var t=localStorage\.getItem\('theme'\).*?</script>\n)")
CANONICAL = re.compile(r'(<link rel="canonical" href="[^"]*">\n)')


def place_markers(text, path):
    """Return text with one pair of each marker in <head>, adding them when absent."""
    if START not in text or END not in text:
        head_end = text.index("</head>")
        head, rest = text[:head_end], text[head_end:]
        markers = START + END + "\n"
        if LEGACY.search(head):
            head = LEGACY.sub(markers, head, count=1)
        elif THEME.search(head):
            head = THEME.sub(lambda m: m.group(1) + markers, head, count=1)
        else:
            raise SystemExit("%s: no place for the jsonld markers" % path)
        text = head + rest

    if OG_START not in text or OG_END not in text:
        head_end = text.index("</head>")
        head, rest = text[:head_end], text[head_end:]
        markers = OG_START + OG_END + "\n"
        if not CANONICAL.search(head):
            raise SystemExit("%s: no place for the og markers" % path)
        head = CANONICAL.sub(lambda m: m.group(1) + markers, head, count=1)
        text = head + rest
    return text


REGION = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
OG_REGION = re.compile(re.escape(OG_START) + r".*?" + re.escape(OG_END), re.S)


def pages():
    for path in sorted(ROOT.glob("*.html")) + sorted(ROOT.glob("articles/*.html")) \
            + sorted(ROOT.glob("calculators/*.html")):
        if path.name in SKIP and path.parent == ROOT:
            continue
        yield path


def sync(path):
    original = path.read_text(encoding="utf-8")
    text = place_markers(original, path)
    data = page_data(text, path)
    text = REGION.sub(lambda m: render_jsonld(data), text, count=1)
    text = OG_REGION.sub(lambda m: render_og(data), text, count=1)
    return original, text


def main():
    ap = argparse.ArgumentParser(
        description="Sync the JSON-LD and Open Graph regions in every page.")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any page's rendered region is stale")
    args = ap.parse_args()

    stale, written = [], []
    for path in pages():
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
