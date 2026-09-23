#!/usr/bin/env python3
"""Write sitemap.xml, with a real <lastmod> on every entry.

    python3 tools/sync_sitemap.py           # rewrite sitemap.xml
    python3 tools/sync_sitemap.py --check   # exit 1 if sitemap.xml has drifted

The old sitemap was hand-written and carried no <lastmod> at all, so a crawler
had nothing to tell a changed page from an untouched one.

The date comes from git, not from the filesystem: a fresh clone stamps every
file with the checkout time, which would claim the whole site changed at once.
A file with uncommitted work has no commit date yet, so that one falls back to
its mtime.

`priority` follows nav_data, so the rail and the sheet cannot disagree:

    1.0  the homepage
    0.9  the eight calculators on the rail
    0.8  every other calculator
    0.6  an article
    0.3  about
    0.2  terms and privacy

404.html stays out, and so does the privacy-policy.html redirect stub, which
carries `noindex`.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nav_data as D  # noqa: E402
from sync_jsonld import ROOT, SITE, file_dates  # noqa: E402

OUT = ROOT / "sitemap.xml"
SKIP = {"404.html", "privacy-policy.html", "sitemap.xml"}

RAIL = {t["href"] for t in [x for x in D.TOOLS if x["tier"] == 1][:8]}


def entry_for(path):
    """Return (loc, changefreq, priority) for one page, or None to skip it."""
    rel = path.relative_to(ROOT).as_posix()
    if path.name in SKIP:
        return None
    if rel == "index.html":
        return (SITE + "/", "monthly", "1.0")
    href = "/" + rel
    if rel.startswith("calculators/"):
        return (SITE + href, "monthly", "0.9" if href in RAIL else "0.8")
    if rel.startswith("articles/"):
        return (SITE + href, "yearly", "0.6")
    if rel == "about.html":
        return (SITE + href, "yearly", "0.3")
    if rel in ("terms.html", "privacy.html"):
        return (SITE + href, "yearly", "0.2")
    return None


def pages():
    yield ROOT / "index.html"
    for pattern in ("*.html", "calculators/*.html", "articles/*.html"):
        for path in sorted(ROOT.glob(pattern)):
            if path.name != "index.html":
                yield path


def render():
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path in pages():
        item = entry_for(path)
        if not item:
            continue
        loc, freq, priority = item
        lastmod = file_dates(path)[1]
        lines.append("  <url><loc>%s</loc><lastmod>%s</lastmod>"
                     "<changefreq>%s</changefreq><priority>%s</priority></url>"
                     % (loc, lastmod, freq, priority))
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Sync sitemap.xml.")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if sitemap.xml has drifted")
    args = ap.parse_args()

    text = render()
    current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    if text == current:
        print("sitemap.xml is up to date")
        return 0
    if args.check:
        print("sitemap.xml is stale")
        print("run: python3 tools/sync_sitemap.py")
        return 1
    OUT.write_text(text, encoding="utf-8")
    print("wrote sitemap.xml with %d url(s)" % text.count("<url>"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
