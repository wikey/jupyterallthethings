# Agent environment guide

This guide is the durable operating procedure for agents that set up or maintain the workshop on a user’s computer. It optimizes for a macOS user who opens notebooks by double-clicking them and never needs to manage Python directly.

## Intended architecture

| Layer | Purpose |
| --- | --- |
| Apple Command Line Tools | Supplies the macOS developer utilities required by Homebrew; full Xcode is unnecessary. |
| Homebrew | Installs and updates local development tools. |
| JupyterLab Desktop (`jupyterlab-app`) | Registers `.ipynb` files with macOS and supplies the desktop interface. |
| `uv` | Creates and maintains the isolated Python environment quickly. |
| Project `.venv` | Holds JupyterLab, pandas, Seaborn, and any future analysis libraries. |
| `requirements.txt` | Records direct dependencies needed to reproduce the environment. |
| JupyterLab project setting | Points notebooks in this workshop at `.venv/bin/python`. |

Do not install the Homebrew `jupyterlab` formula for this workflow. That formula provides the command-line/web application, not the desktop file-opening experience.

## First-time macOS setup

### Preconditions

- macOS 12 or newer
- A local agent with permission to run shell commands
- The complete workshop downloaded, unzipped, and moved to a stable location
- Internet access during installation

Apple Command Line Tools do not need to be installed in advance. If they are missing, the agent can open Apple’s official installer, but the user must approve the macOS dialog and wait for it to finish. Full Xcode is not required.

The installation downloads software from Apple, Homebrew, and Python package registries. It does not need to read or transmit assessment data.

### Preferred procedure

From the workshop root, review and run:

```bash
bash scripts/setup_macos.sh
```

The script performs these operations idempotently:

1. Confirms that it is running on macOS 12 or newer.
2. Verifies Apple Command Line Tools and opens Apple’s installer when they are missing.
3. Confirms that Homebrew is available.
4. Installs or updates JupyterLab Desktop, `uv`, and `duti` through Homebrew.
5. Creates `.venv` with Python 3.12 if it does not exist.
6. Installs `requirements.txt` into that environment, including Seaborn.
7. Verifies imports without reading workshop data.
8. Sets JupyterLab Desktop’s project-specific `pythonPath` for `notebooks/`.
9. Makes JupyterLab Desktop the default application for `.ipynb` files.
10. Opens the first notebook in JupyterLab Desktop.

If Apple Command Line Tools are missing, the script runs `xcode-select --install` and stops. Tell the user to click **Install**, accept Apple’s license, and provide approval if requested. Wait for installation to finish, verify `xcode-select -p` and `xcrun --find clang`, and run the script again. Do not install the full Xcode application.

If Homebrew is missing, explain what Homebrew is and ask the user to approve its installation. Use only the official installer from <https://brew.sh/>. After Homebrew is installed, run the setup script again.

### Configuration performed by the script

The essential JupyterLab Desktop command is:

```bash
jlab config set pythonPath \
  "/absolute/path/to/workshop/.venv/bin/python" \
  --project-path="/absolute/path/to/workshop/notebooks"
```

JupyterLab Desktop treats the parent directory of a double-clicked notebook as its project directory. Since all workshop notebooks live in `notebooks/`, this project setting makes every notebook use the same environment.

The essential Finder association is:

```bash
duti -s org.jupyter.jupyterlab-desktop .ipynb all
```

## Verify setup without opening data

Run these checks from the workshop root:

```bash
.venv/bin/python -c "import IPython, ipywidgets, jupyterlab, matplotlib, nbformat, numpy, pandas, seaborn; print('Workshop imports: OK')"

JLAB_CLI="$(command -v jlab || true)"
if [[ -z "$JLAB_CLI" ]]; then
  JLAB_CLI="/Applications/JupyterLab.app/Contents/Resources/app/jlab"
fi
"$JLAB_CLI" config list --project-path="$PWD/notebooks"

duti -x ipynb
```

Success means:

- the import command exits successfully;
- the project configuration reports `.venv/bin/python`; and
- `duti` reports JupyterLab as the handler for `.ipynb`.

Do not use a notebook execution as the environment’s first verification step.

## Add an analysis or visualization library

Suppose the user asks for Plotly. Work from the workshop root.

1. Add a direct dependency to `requirements.txt`, for example:

   ```text
   plotly>=6.0
   ```

2. Reconcile the environment from the complete requirements file:

   ```bash
   uv pip install --python .venv/bin/python --requirement requirements.txt
   ```

3. Verify the import and version without reading data:

   ```bash
   .venv/bin/python -c "import importlib.metadata as m, plotly; print('plotly', m.version('plotly'))"
   ```

4. Tell the user to select **Kernel → Restart Kernel** in an open notebook.

Use the package’s distribution name in `requirements.txt`; verify using its actual import name. They can differ—for example, the distribution `scikit-learn` is imported as `sklearn`.

Prefer libraries that work without separately compiled JupyterLab extensions. Modern packages such as Plotly, Altair, OpenPyXL, PyArrow, Statsmodels, and scikit-learn generally work well in this model, but confirm current compatibility before installation.

## Remove a library

1. Confirm that no notebook imports it.
2. Remove its direct entry from `requirements.txt`.
3. Remove it from the environment:

   ```bash
   uv pip uninstall --python .venv/bin/python PACKAGE_NAME
   ```

4. Run import and notebook checks appropriate to the change.

Do not remove transitive packages speculatively.

## Repair or relocate the workshop

### Workshop moved to another folder

The `.venv` contains absolute paths and JupyterLab’s project setting is path-specific. Run:

```bash
rm -rf .venv
bash scripts/setup_macos.sh
```

Only remove `.venv`; do not delete notebooks, CSV files, or JupyterLab application data.

### Package installation is inconsistent

First reconcile the existing environment:

```bash
uv pip install --python .venv/bin/python --requirement requirements.txt
```

If verification still fails, rebuild only the environment:

```bash
rm -rf .venv
bash scripts/setup_macos.sh
```

### Double-click opens another application

Reapply and inspect the association:

```bash
duti -s org.jupyter.jupyterlab-desktop .ipynb all
duti -x ipynb
```

The equivalent Finder operation is **Get Info → Open with → JupyterLab → Change All**.

### Notebook uses the wrong Python environment

Re-run `scripts/setup_macos.sh`. In JupyterLab Desktop, the environment shown in the title bar should resolve to the workshop’s `.venv`. The user can also select it from the environment control in the title bar.

## Notebook and publication checks

Environment maintenance does not require notebook execution. When a package or code change does require execution:

- use only the committed synthetic CSV files;
- execute notebooks from the `notebooks/` directory or workshop root;
- fail on exceptions;
- inspect saved outputs for direct identifiers before committing; and
- rebuild the static site with `python scripts/build_site.py`.

Never execute or publish notebooks containing real student records as part of repository maintenance.
