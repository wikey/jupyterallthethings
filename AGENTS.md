# Instructions for local coding agents

This repository is a local-first Jupyter workshop for people who should not need to know Python. Your role is to handle environment setup and code changes while the user supplies questions, domain judgment, and interpretation.

## Read first

Before changing the environment or notebooks, read:

1. `README.md`
2. `docs/agent-environment-guide.md`
3. `requirements.txt`

## Data boundary

- Treat all assessment files as sensitive, even though the files committed to this repository are synthetic.
- Do not upload, transmit, paste, summarize, or send CSV contents, notebook outputs, names, identifiers, or row samples to an LLM or any remote service.
- Environment setup never requires reading the CSV contents. Verify packages with import checks instead.
- Notebook code must perform analysis locally and must not make network or AI API calls.
- Do not publish notebook output derived from real student data.

## Environment policy

On macOS:

- Install the desktop application with the Homebrew cask `jupyterlab-app`; do not substitute the `jupyterlab` formula.
- Use `uv` and the project-local `.venv` for Python packages.
- Never install workshop packages into macOS system Python, Homebrew’s global Python, or JupyterLab Desktop’s bundled environment.
- Configure JupyterLab Desktop’s `pythonPath` for the `notebooks/` project directory.
- Associate `.ipynb` files with the JupyterLab Desktop bundle ID `org.jupyter.jupyterlab-desktop`.
- Use `scripts/setup_macos.sh` for initial setup or repair rather than improvising a parallel installation.

## Adding or changing libraries

When a user requests another analysis or visualization library:

1. Confirm the package is appropriate and identify both its distribution name and import name.
2. Add the direct dependency to `requirements.txt` with a reasonable lower bound. Do not freeze unrelated transitive dependencies.
3. Install it with `uv pip install --python .venv/bin/python --requirement requirements.txt`.
4. Verify the import and report the installed version without opening any data file.
5. Tell the user to restart the notebook kernel if JupyterLab Desktop is already open.
6. If notebook code changes, run the affected notebooks against synthetic data only and inspect saved outputs for errors or accidental identifier display.

Follow the detailed recipes and recovery steps in `docs/agent-environment-guide.md`.

## Static site

- `python scripts/build_site.py` renders saved outputs; it must not execute notebooks.
- `_site/` is generated and must remain uncommitted.
- Run the site build and link validation after changing documentation, notebooks, downloads, or navigation.
