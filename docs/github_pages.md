# Publishing Documentation to GitHub Pages

This guide explains how to publish your Sphinx documentation to GitHub Pages for the BinaryOptionsTools project.

## 1. Build the HTML Documentation

From the project root, run:

```bash
cd docs
make html
```

The HTML files will be generated in `docs/build/html/`.

## 2. Push the HTML to the `gh-pages` Branch

You can use the `ghp-import` tool to easily publish the HTML build:

```bash
pip install ghp-import
cd docs
# This will push the HTML to the gh-pages branch
ghp-import -n -p -f build/html
```

- `-n`: Include a .nojekyll file (recommended for Sphinx)
- `-p`: Push to origin/gh-pages
- `-f`: Force overwrite

## 3. Enable GitHub Pages in Repository Settings

- Go to your repository on GitHub.
- Click **Settings** > **Pages**.
- Under **Source**, select the `gh-pages` branch and `/ (root)`.
- Save.

Your documentation will be available at `https://<username>.github.io/<repo>/`.

## 4. (Optional) Add a Docs Badge to README

Add this to your `README.md`:

```markdown
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://<username>.github.io/<repo>/)
```
