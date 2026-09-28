# Local, research-grade analysis of student assessment data

A five-part Jupyter workshop showing how Python can turn raw assessment exports into careful, research-grade explorations while the data stays on the analyst’s machine.

The audience is not programmers. It is domain experts—assessment coordinators, research directors, program staff, and others—who are comfortable asking an AI assistant for help but may not yet realize that an agent can support the entire local workflow. The included CSV files are synthetic.

## Workshop sequence

Read and run the notebooks in order:

1. [`00_research_wow.ipynb`](notebooks/00_research_wow.ipynb) — reproduce a landmark education-research pattern.
2. [`01_local_first_look.ipynb`](notebooks/01_local_first_look.ipynb) — load and inspect assessment exports without exposing identifiers.
3. [`02_clean_analysis_table.ipynb`](notebooks/02_clean_analysis_table.ipynb) — validate joins and build a clean longitudinal table.
4. [`03_exploratory_growth.ipynb`](notebooks/03_exploratory_growth.ipynb) — explore cohort trends, paired growth, and subgroup summaries.
5. [`04_presentation_view.ipynb`](notebooks/04_presentation_view.ipynb) — produce an aggregate, presentation-ready dashboard.

Realistic prompts between steps demonstrate how to ask an AI assistant for generic code using a schema description rather than student records.

## Run the workshop locally

Python 3.10 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
jupyter lab
```

Open `notebooks/00_research_wow.ipynb` and run the cells from top to bottom. Keep the notebooks and CSV files in their existing folders so the notebooks can locate the data.

## Build and preview the static site

The site builder converts the notebooks’ **saved content and outputs** to HTML. It does not execute notebook code or process the CSV files.

```bash
python scripts/build_site.py
python -m http.server --directory _site 8000
```

Open <http://localhost:8000>. The generated `_site/` directory contains:

- a workshop landing page;
- five linked, static notebook lessons;
- downloadable source notebooks and synthetic CSV files; and
- a ZIP containing the complete local workshop.

The build fails if a notebook contains saved error output or if the generated site contains a broken local link. `_site/` is generated and intentionally excluded from version control.

## Publish with GitHub Pages

This directory is ready to serve as the root of a standalone GitHub repository.

1. Create an empty GitHub repository.
2. Push the contents of this directory to its `main` branch.
3. In **Settings → Pages**, set **Source** to **GitHub Actions** if it is not already selected.
4. Open the **Actions** tab and watch the “Deploy workshop to GitHub Pages” workflow.

The workflow in `.github/workflows/deploy-pages.yml` builds and deploys `_site/` on every push to `main`. It can also be run manually from the Actions tab. All site links are relative, so the result works at either a user/organization Pages domain or a project subpath.

## Data-handling note

The notebooks make no network or AI calls; every calculation runs locally. An LLM’s role is to help write generic code from a schema description, never to receive student records.

Local processing is not automatically policy-compliant. Use an approved device and environment, follow your organization’s student-data rules, and inspect all saved notebook outputs before publishing a derivative site. **Only synthetic data is included in this package.**

## Repository structure

```text
.
├── .github/workflows/deploy-pages.yml  # Automated GitHub Pages deployment
├── assets/site.css                     # Shared site styles
├── notebooks/                          # Workshop source notebooks
├── scripts/build_site.py               # Static-site builder
├── FakeiReadyData.csv                  # Synthetic Reading export
├── FakeiReadyMathData.csv              # Synthetic Math export
├── FakeiReadySchema.csv                # Data dictionary/schema
├── requirements.txt                    # Local and site-build dependencies
└── README.md
```
