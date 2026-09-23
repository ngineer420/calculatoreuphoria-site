# Deploying calculatoreuphoria.com

This repo is live. `origin` points at
`https://github.com/ngineer420/calculatoreuphoria-site`, GitHub Pages serves
the `main` branch, and the site answers at https://calculatoreuphoria.com.

Sections 2 and 3 record how that was set up. Read them when you repoint DNS or
rebuild the Pages configuration. To ship a change, push a branch and open a
pull request. A merge to `main` deploys within a minute or two.

## 1. Push a change

```
git checkout -b fix/<short-topic>
python3 tools/sync_nav.py
python3 tools/sync_jsonld.py
python3 tools/sync_sitemap.py
git commit -am "<what changed>"
git push -u origin fix/<short-topic>
gh pr create
```

Run the three generators before every commit. Each one takes `--check`, which
exits 1 when a file has drifted.

## 2. Enable GitHub Pages

In the new repo: **Settings → Pages** → Source: "Deploy from a branch" →
Branch: `main`, folder `/ (root)`. GitHub will build and serve the site at
`https://<your-username>.github.io/calculatoreuphoria-site/` within a minute
or two.

## 3. Point calculatoreuphoria.com at GitHub Pages

Log in to whichever registrar/DNS provider manages `calculatoreuphoria.com`
and edit its DNS records.

### Apex domain (`calculatoreuphoria.com`) — required

Add four **A** records, all at the root (`@` / blank host):

| Type | Host | Value            |
|------|------|------------------|
| A    | @    | 185.199.108.153  |
| A    | @    | 185.199.109.153  |
| A    | @    | 185.199.110.153  |
| A    | @    | 185.199.111.153  |

Optional but recommended — IPv6 **AAAA** records for the same root:

| Type | Host | Value                 |
|------|------|------------------------|
| AAAA | @    | 2606:50c0:8000::153    |
| AAAA | @    | 2606:50c0:8001::153    |
| AAAA | @    | 2606:50c0:8002::153    |
| AAAA | @    | 2606:50c0:8003::153    |

### `www` subdomain — optional, recommended

| Type  | Host | Value                         |
|-------|------|-------------------------------|
| CNAME | www  | `<your-username>.github.io`   |

The repo's `CNAME` file is already set to `calculatoreuphoria.com`, so GitHub
Pages treats the apex as canonical. Don't delete that file — Pages uses it
to provision the HTTPS certificate for the custom domain.

DNS propagation can take anywhere from a few minutes to 24–48 hours. Once it
resolves, go to **Settings → Pages** and check "Enforce HTTPS".

## 4. Verify

Visit `https://calculatoreuphoria.com` and spot-check a few calculators
(mortgage, BMI, scientific) on both desktop and mobile widths, and toggle
dark mode.

## 5. Monetization (optional)

Calculator sites are typically monetized with display ads (Google AdSense)
rather than affiliate links, since there's no natural product tie-in. If you
want to apply:

1. The site needs to be live at the custom domain with real, working content
   for a period before most ad networks approve it — this repo's 12
   calculators plus About/Privacy/Terms pages are meant to clear that bar.
2. Apply at https://www.google.com/adsense/ using your own account details
   (Claude/this agent never touches this step).
3. Once approved, add your AdSense snippet to the `<head>` of each page, or
   ask for it to be templated in — happy to wire that up on request.
4. Keep the Privacy Policy page (`privacy.html`) accurate about ad
   cookies — it already has a placeholder section for this.

## 6. Ongoing

- New calculators should be added following the pattern in `README.md`.
- Update `sitemap.xml` whenever a new calculator page is added.
