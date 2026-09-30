# Local, research-grade analysis of student assessment data

Python running on your computer gives you private, professional-grade analysis. You do not need to know—or learn—Python to use it: a local agent can write, run, and revise the code while you guide the questions, review the work, and interpret the results.

This five-part Jupyter workshop is designed for assessment coordinators, research directors, program staff, and other domain experts. It turns raw assessment exports into careful explorations while the data stays on the analyst’s machine. The included CSV files are synthetic.

## Workshop sequence

Read and run the notebooks in order:

1. [`00_research_wow.ipynb`](notebooks/00_research_wow.ipynb) — reproduce a landmark education-research pattern.
2. [`01_local_first_look.ipynb`](notebooks/01_local_first_look.ipynb) — load and inspect assessment exports without exposing identifiers.
3. [`02_clean_analysis_table.ipynb`](notebooks/02_clean_analysis_table.ipynb) — validate joins and build a clean longitudinal table.
4. [`03_exploratory_growth.ipynb`](notebooks/03_exploratory_growth.ipynb) — explore cohort trends, paired growth, and subgroup summaries.
5. [`04_presentation_view.ipynb`](notebooks/04_presentation_view.ipynb) — produce an aggregate, presentation-ready dashboard.

Realistic prompts between steps demonstrate how to ask an AI assistant for generic code using a schema description rather than student records.

## Recommended Mac setup: ask a local agent

The intended macOS experience is a one-time agent-assisted installation followed by double-clicking notebook files in Finder.

1. Download and unzip the complete workshop.
2. Move the workshop to a stable location.
3. Open [`prompts/macos-setup-agent-prompt.md`](prompts/macos-setup-agent-prompt.md).
4. Paste the complete prompt into a local agent with permission to run shell commands.
5. Follow any macOS approval prompts described by the agent.
6. Double-click `notebooks/00_research_wow.ipynb`.

The agent uses the included [`scripts/setup_macos.sh`](scripts/setup_macos.sh) to install:

- JupyterLab Desktop through the Homebrew cask `jupyterlab-app`;
- `uv` for an isolated project environment;
- all libraries in `requirements.txt`, including Seaborn; and
- `duti` to make JupyterLab Desktop the default `.ipynb` application.

It then configures notebooks in this workshop to use `.venv/bin/python`. Setup downloads software but does not need to inspect or transmit assessment data.

Instructions for future agents—including adding libraries, repairing the environment, handling a moved folder, and preserving the local-data boundary—are in [`AGENTS.md`](AGENTS.md) and [`docs/agent-environment-guide.md`](docs/agent-environment-guide.md).

For example, a user can later tell their agent:

> Add Plotly and OpenPyXL to this workshop. Record them in its requirements, install them into the project environment, verify the imports without opening data, and tell me when to restart the notebook kernel.

## Manual setup or non-macOS environments

Python 3.10 or newer is recommended. Users who prefer a command-line setup can run:

```bash
python3 -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
jupyter lab
```

Keep the notebooks and CSV files in their existing folders so the notebooks can locate the data.

## Build and preview the static site

The site builder converts the notebooks’ **saved content and outputs** to HTML. It does not execute notebook code or process the CSV files.

```bash
python scripts/build_site.py
python -m http.server --directory _site 8000
```

Open <http://localhost:8000>. The generated `_site/` directory contains:

- a workshop landing page;
- a copyable Mac setup prompt;
- five linked, static notebook lessons;
- downloadable source notebooks and synthetic CSV files; and
- a ZIP containing the complete local workshop and agent documentation.

The build fails if a notebook contains saved error output or if the generated site contains a broken local link. `_site/` is generated and intentionally excluded from version control.

## Publish with GitHub Pages

The workflow in `.github/workflows/deploy-pages.yml` builds and deploys `_site/` on every push to `main`. It can also be run manually from the Actions tab. All site links are relative, so the result works at either a user/organization Pages domain or a project subpath.

## Data-handling note

The notebooks make no network or AI calls; every calculation runs locally. An LLM’s role is to help write generic code from a schema description, never to receive student records.

Local processing is not automatically policy-compliant. Use an approved device and environment, follow your organization’s student-data rules, and inspect all saved notebook outputs before publishing a derivative site. **Only synthetic data is included in this package.**

## Repository structure

```text
.
├── .github/workflows/deploy-pages.yml  # Automated GitHub Pages deployment
├── AGENTS.md                           # Durable instructions for local agents
├── assets/site.css                     # Shared site styles
├── docs/agent-environment-guide.md     # Setup, library, repair, and privacy procedures
├── notebooks/                          # Workshop source notebooks
├── prompts/macos-setup-agent-prompt.md # Copyable setup prompt
├── scripts/build_site.py               # Static-site builder
├── scripts/setup_macos.sh              # Idempotent macOS setup
├── FakeiReadyData.csv                  # Synthetic Reading export
├── FakeiReadyMathData.csv              # Synthetic Math export
├── FakeiReadySchema.csv                # Data dictionary/schema
├── requirements.txt                    # Reproducible project dependencies
└── README.md
```
