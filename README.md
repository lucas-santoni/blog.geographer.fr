# [blog.geographer.fr](https://blog.geographer.fr/)

Personal blog by Lucas SANTONI. Built with [Astro](https://astro.build/),
deployed on [Vercel](https://vercel.com/).

---

## Quickstart

```sh
nvm use            # picks up .node-version
npm install
npm run dev        # http://localhost:4321
```

Push to `master` → Vercel deploys automatically. Pull requests get preview
URLs.

---

## Local preview & build

```sh
npm run dev        # dev server with hot reload
npm run build      # type-check + static build → dist/
npm run preview    # serve dist/ locally
npm run lint       # ESLint
```

`npm run build` runs `astro check` (TypeScript + Astro template type check)
before building. Vercel runs the same on every deploy, so type errors fail
the deploy and never reach production.

`npm run lint` is **advisory only** — it is not part of `build`. CI
(`.github/workflows/ci.yml`) runs both lint and check on every push and PR
as a status check, but lint failures **do not** block Vercel deploys.
Rationale: for a personal blog, blocking a deploy on a stylistic warning
(unused import, missing semicolon) is friction without value. Type errors
would actually break the site, so those still gate deploys via
`astro check`.

---

## Writing a new post

```sh
npm run new "My new post title"
```

This scaffolds `src/content/posts/<slug>.md` with the right frontmatter and
today's date. Open it, write Markdown, save. Code blocks get syntax
highlighting (Shiki, build-time, no client JS).

The frontmatter looks like:

```yaml
---
title: "My new post title"
slug: my-new-post-title
date: 2026-04-29
description: "Optional. Used for OG cards, RSS, and meta description."
cover: "assets/my-post/cover.png"  # Optional. Path under public/.
---
```

**Field reference:**

| Field | Required | Notes |
|---|---|---|
| `title` | yes | Quote with `"..."` if it contains a colon. |
| `slug` | yes | URL path. `slug: foo` produces `/foo`. |
| `date` | yes (posts only) | `YYYY-MM-DD` or full ISO datetime. Newest first on the homepage. |
| `description` | no | Short summary for OG/RSS/meta. |
| `cover` | no | OG/Twitter image, root-relative. |

The same applies for pages in `src/content/pages/`, except `date` is not used.

---

## Adding images

Drop them in `public/assets/<post-slug>/` and reference with a **leading
slash**:

```markdown
![alt](/assets/my-post/diagram.png)
```

Files in `public/` are copied verbatim to the site root.

---

## Editing the obvious things

| What | Where |
|---|---|
| Site name, intro, email, GitHub link | `src/config.ts` |
| Featured projects on the homepage | `src/data/projects.ts` |
| Resume content | `src/pages/resume.astro` |
| About page | `src/content/pages/about.md` |
| 404 page text | `src/content/pages/404.md` |
| Theme CSS | `src/styles/styles.css` (and `resume.css` for the resume) |
| Site head metadata, OG defaults, etc. | `src/layouts/Base.astro` |
| Sitemap excludes / change frequency / priority | `astro.config.mjs` |

---

## Project layout

```
src/
  config.ts            site-wide constants
  content.config.ts    Astro content collection schemas
  content/
    posts/             one Markdown file per blog post
    pages/             non-post pages (about, 404, resume content, etc.)
  data/projects.ts     featured projects on the homepage
  layouts/Base.astro   shared <head>, header, footer
  pages/               URL routes (Astro auto-routes)
  styles/              global CSS
  utils/               small helpers (date formatting, smart title break)
public/                assets and root files (favicon, robots.txt, manifest…)
scripts/new-post.mjs   `npm run new` scaffold
astro.config.mjs       Astro + Vercel + sitemap config
```

---

## License

Source code and code snippets in posts are [MIT](LICENSE). Blog prose and
authored images are [CC BY 4.0](LICENSE-CONTENT) — reuse them, just credit me.
