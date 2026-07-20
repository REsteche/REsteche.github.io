# resteche.github.io

Personal website of **Ruben Esteche** — Staff ML/AI Engineer specializing in NLP, LLMs, RAG systems and MLOps.

Live at **[resteche.github.io](https://resteche.github.io/)**.

## Stack

Intentionally simple: static **HTML + CSS + vanilla JavaScript**. No frameworks, no build step, no dependencies to rot.

```
index.html            # single-page site (hero, about, experience, projects, stack, research, education, contact)
404.html              # custom not-found page
assets/css/style.css  # design system (dark AI theme, CSS custom properties)
assets/css/blog.css   # blog index + notebook post styling
assets/js/main.js     # neural-network canvas, typewriter, scroll reveals, live GitHub stars
assets/img/           # favicon and graphics
images/               # photos and research figures
files/                # resume PDF and downloadable documents
notebooks/            # blog posts as Jupyter notebooks (source of truth)
blog/                 # generated blog HTML — do not edit by hand
scripts/build_blog.py # notebook → HTML converter (nbconvert)
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

Posts are written as Jupyter notebooks in `notebooks/` (migrated from the old [REsteche_blog](https://github.com/REsteche/REsteche_blog) fastpages repo, original dates preserved) and converted to styled HTML in `blog/` by a local script.

### Writing a new post

1. Create `notebooks/YYYY-MM-DD-my-post.ipynb` — the date in the filename is the publication date.
2. Make the **first cell** a markdown cell with the post's front matter:

   ```markdown
   # My Post Title
   > One-sentence description shown on the blog index.

   - categories: [Machine Learning, Python]
   ```

3. Write the post in the cells below (markdown, code, plots, LaTeX math — all supported). Cells starting with `#hide` are excluded from the output.
4. Build and preview:

   ```bash
   ./build_blog.sh     # converts notebooks → blog/ (creates a one-time venv with nbconvert)
   ./serve.sh          # preview at http://localhost:8000/blog/
   ```

5. Commit both the notebook and the generated `blog/` files, then push — GitHub Pages publishes them as-is.

Relative images should live in a folder inside `notebooks/` (e.g. `posts_images/`); the build copies those folders next to the generated posts.
