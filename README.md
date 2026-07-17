# resteche.github.io

Personal website of **Ruben Esteche** — Staff ML/AI Engineer specializing in NLP, LLMs, RAG systems and MLOps.

Live at **[resteche.github.io](https://resteche.github.io/)**.

## Stack

Intentionally simple: static **HTML + CSS + vanilla JavaScript**. No frameworks, no build step, no dependencies to rot.

```
index.html            # single-page site (hero, about, experience, projects, stack, research, education, contact)
404.html              # custom not-found page
assets/css/style.css  # design system (dark AI theme, CSS custom properties)
assets/js/main.js     # neural-network canvas, typewriter, scroll reveals, live GitHub stars
assets/img/           # favicon and graphics
images/               # photos and research figures
files/                # resume PDF and downloadable documents
.nojekyll             # tells GitHub Pages to serve files as-is (skip Jekyll)
```

## Deployment

Deployed by **GitHub Pages** from the `master` branch — the same pipeline as before:

1. Push (or merge a PR) to `master`.
2. The automatic `pages-build-deployment` workflow picks up the change.
3. The site updates at resteche.github.io within a minute or two.

The `.nojekyll` file skips the Jekyll build entirely, so deploys are faster and what you commit is exactly what gets served.

## Local development

No install step — the site is plain HTML/CSS/JS. The only requirement is Python 3 (already on macOS).

```bash
./serve.sh          # opens http://localhost:8000
./serve.sh 4000     # custom port
```

Or, without the script:

```bash
python3 -m http.server 8000
```

## Blog

The blog lives in a separate repository ([REsteche_blog](https://github.com/REsteche/REsteche_blog)) and is linked from the site's navigation.
