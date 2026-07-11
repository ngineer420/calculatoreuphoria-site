# Deploying calculatoreuphoria.com

This repo is built and committed locally, but **not yet pushed to GitHub** —
the `gh` CLI on this machine has an expired token, so the remote repo needs
to be created manually (or re-auth `gh` and it can be done in one command).

## 1. Create the GitHub repo and push

Option A — re-authenticate `gh` first, then let it create + push in one step:

```
gh auth refresh -h github.com
gh repo create calculatoreuphoria-site --public --source=. --remote=origin --push
```

Option B — create the repo manually on github.com (Settings → your account →
New repository, name it e.g. `calculatoreuphoria-site`, public, no README/
.gitignore/license), then:

```
git remote add origin https://github.com/<your-username>/calculatoreuphoria-site.git
git push -u origin main
```

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
4. Keep the Privacy Policy page (`privacy-policy.html`) accurate about ad
   cookies — it already has a placeholder section for this.

## 6. Ongoing

- New calculators should be added following the pattern in `README.md`.
- Update `sitemap.xml` whenever a new calculator page is added.
