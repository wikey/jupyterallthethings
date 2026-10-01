#!/usr/bin/env bash
# Configure a private, project-local JupyterLab Desktop environment on macOS.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NOTEBOOKS_DIR="$ROOT/notebooks"
FIRST_NOTEBOOK="$NOTEBOOKS_DIR/00_research_wow.ipynb"
VENV="$ROOT/.venv"
PYTHON="$VENV/bin/python"

fail() {
  printf 'Setup stopped: %s\n' "$1" >&2
  exit 1
}

[[ "$(uname -s)" == "Darwin" ]] || fail "this setup script supports macOS only."

MACOS_VERSION="$(sw_vers -productVersion)"
MACOS_MAJOR="${MACOS_VERSION%%.*}"
(( MACOS_MAJOR >= 12 )) || fail "JupyterLab Desktop requires macOS 12 or newer; found $MACOS_VERSION."

printf '\n[1/7] Checking Apple Command Line Tools...\n'
DEVELOPER_DIR="$(xcode-select -p 2>/dev/null || true)"
if [[ -z "$DEVELOPER_DIR" ]] || [[ ! -d "$DEVELOPER_DIR" ]] || ! xcrun --find clang >/dev/null 2>&1; then
  printf '%s\n' \
    "Apple Command Line Tools are required by Homebrew; full Xcode is not required." \
    "Requesting Apple’s official installer now."
  xcode-select --install >/dev/null 2>&1 || true
  fail "complete the Command Line Tools installation in the macOS dialog, verify it has finished, and run this script again."
fi
printf 'Apple developer tools: %s\n' "$DEVELOPER_DIR"

# Homebrew may be installed but absent from a non-interactive agent's PATH.
if ! command -v brew >/dev/null 2>&1; then
  for candidate in /opt/homebrew/bin/brew /usr/local/bin/brew; do
    if [[ -x "$candidate" ]]; then
      eval "$("$candidate" shellenv)"
      break
    fi
  done
fi
command -v brew >/dev/null 2>&1 || fail "Homebrew is not installed. Ask the user to approve installation from https://brew.sh/, then run this script again."

for required in \
  "$ROOT/requirements.txt" \
  "$ROOT/AGENTS.md" \
  "$ROOT/docs/agent-environment-guide.md" \
  "$FIRST_NOTEBOOK"; do
  [[ -f "$required" ]] || fail "required workshop file not found: $required"
done

printf '\n[2/7] Installing the desktop application and environment tools...\n'
brew install --cask jupyterlab-app
brew install uv duti

printf '\n[3/7] Creating the project-local Python environment...\n'
if [[ ! -x "$PYTHON" ]]; then
  uv venv --python 3.12 "$VENV"
fi

printf '\n[4/7] Installing the recorded workshop requirements...\n'
uv pip install --python "$PYTHON" --requirement "$ROOT/requirements.txt"

printf '\n[5/7] Verifying required imports without opening workshop data...\n'
"$PYTHON" - <<'PY'
import importlib
import importlib.metadata

checks = {
    "IPython": "ipython",
    "ipywidgets": "ipywidgets",
    "jupyterlab": "jupyterlab",
    "matplotlib": "matplotlib",
    "nbformat": "nbformat",
    "numpy": "numpy",
    "pandas": "pandas",
    "seaborn": "seaborn",
}
for import_name, distribution_name in checks.items():
    importlib.import_module(import_name)
    version = importlib.metadata.version(distribution_name)
    print(f"{distribution_name} {version}")
PY

printf '\n[6/7] Configuring JupyterLab Desktop and Finder...\n'
JLAB_CLI="$(command -v jlab || true)"
if [[ -z "$JLAB_CLI" ]]; then
  JLAB_CLI="/Applications/JupyterLab.app/Contents/Resources/app/jlab"
fi
[[ -x "$JLAB_CLI" ]] || fail "JupyterLab Desktop CLI was not found after installation."

"$JLAB_CLI" config set pythonPath "$PYTHON" --project-path="$NOTEBOOKS_DIR"
duti -s org.jupyter.jupyterlab-desktop .ipynb all

CONFIG_OUTPUT="$("$JLAB_CLI" config list --project-path="$NOTEBOOKS_DIR")"
printf '%s\n' "$CONFIG_OUTPUT"
grep -Fq "$PYTHON" <<<"$CONFIG_OUTPUT" || fail "JupyterLab Desktop did not retain the project Python path."

HANDLER_OUTPUT="$(duti -x ipynb)"
printf '%s\n' "$HANDLER_OUTPUT"
grep -Eiq 'JupyterLab|org\.jupyter\.jupyterlab-desktop' <<<"$HANDLER_OUTPUT" || fail "JupyterLab Desktop is not the registered .ipynb handler."

printf '\n[7/7] Opening the first workshop notebook...\n'
open -a JupyterLab "$FIRST_NOTEBOOK"

cat <<EOF

Setup complete.
Workshop: $ROOT
Environment: $PYTHON
Start next time: double-click notebooks/00_research_wow.ipynb in Finder.
If JupyterLab was already running, restart it before opening the notebook again.
EOF
