#!/usr/bin/env python3
"""Build the workshop as a static, GitHub Pages-ready site.

The builder converts saved notebook content and outputs to HTML. It deliberately
does not execute notebook code, so a deployment never reads or transforms the
source CSV files.
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZIP_DEFLATED, ZipFile

import nbformat
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "_site"

LESSONS = (
    {
        "source": "00_research_wow.ipynb",
        "slug": "00-research-wow.html",
        "number": "00",
        "title": "Research wow",
        "description": "Reproduce a landmark education-research pattern with live charts and an interactive model.",
    },
    {
        "source": "01_local_first_look.ipynb",
        "slug": "01-local-first-look.html",
        "number": "01",
        "title": "Local first look",
        "description": "Load local assessment exports, inspect their structure, and keep identifiers out of view.",
    },
    {
        "source": "02_clean_analysis_table.ipynb",
        "slug": "02-clean-analysis-table.html",
        "number": "02",
        "title": "Build a clean analysis table",
        "description": "Validate joins and reshape two exports into a vetted longitudinal table.",
    },
    {
        "source": "03_exploratory_growth.ipynb",
        "slug": "03-exploratory-growth.html",
        "number": "03",
        "title": "Explore longitudinal growth",
        "description": "Study trends, paired growth, and subgroup patterns without making causal claims.",
    },
    {
        "source": "04_presentation_view.ipynb",
        "slug": "04-presentation-view.html",
        "number": "04",
        "title": "Create a presentation view",
        "description": "Turn reviewed analyses into an aggregate, presentation-ready dashboard.",
    },
)

DATA_FILES = (
    "FakeiReadyData.csv",
    "FakeiReadyMathData.csv",
    "FakeiReadySchema.csv",
)

PACKAGE_FILES = (
    "AGENTS.md",
    "README.md",
    "requirements.txt",
    "docs/agent-environment-guide.md",
    "prompts/macos-setup-agent-prompt.md",
    "scripts/setup_macos.sh",
    *DATA_FILES,
    *(f"notebooks/{lesson['source']}" for lesson in LESSONS),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=BUILD,
        help="Output directory (default: %(default)s)",
    )
    return parser.parse_args()


def require_sources() -> None:
    missing = [relative for relative in PACKAGE_FILES if not (ROOT / relative).is_file()]
    if missing:
        formatted = "\n".join(f"- {path}" for path in missing)
        raise SystemExit(f"Cannot build; required source files are missing:\n{formatted}")


def site_header(prefix: str) -> str:
    return f"""
<a class="skip-link" href="#workshop-content">Skip to content</a>
<header class="site-header" aria-label="Workshop header">
  <div class="site-header__inner">
    <a class="site-brand" href="{prefix}index.html">
      <span class="site-brand__eyebrow">Local-first workshop</span>
      <span class="site-brand__name">Research-grade assessment analysis</span>
    </a>
    <nav class="site-nav" aria-label="Site navigation">
      <a href="{prefix}index.html#lessons">Lessons</a>
      <a href="{prefix}index.html#setup">Run locally</a>
      <a href="{prefix}index.html#downloads">Downloads</a>
    </nav>
  </div>
</header>
<div id="workshop-content" tabindex="-1"></div>
""".strip()


def lesson_footer(index: int) -> str:
    lesson = LESSONS[index]
    previous_link = (
        f'<a class="lesson-nav__link" rel="prev" href="{LESSONS[index - 1]["slug"]}">'
        f'<span>Previous</span><strong>{html.escape(LESSONS[index - 1]["title"])}</strong></a>'
        if index > 0
        else '<a class="lesson-nav__link" href="../index.html"><span>Back to</span><strong>Workshop home</strong></a>'
    )
    next_link = (
        f'<a class="lesson-nav__link lesson-nav__link--next" rel="next" href="{LESSONS[index + 1]["slug"]}">'
        f'<span>Next</span><strong>{html.escape(LESSONS[index + 1]["title"])}</strong></a>'
        if index < len(LESSONS) - 1
        else '<a class="lesson-nav__link lesson-nav__link--next" href="../index.html#downloads"><span>Finish with</span><strong>Workshop downloads</strong></a>'
    )
    return f"""
<section class="lesson-tools" aria-label="Lesson resources">
  <p><strong>Part {index + 1} of {len(LESSONS)}</strong> · Read the saved output here, or download the notebook to run and change it locally.</p>
  <a class="button button--small" href="../downloads/notebooks/{lesson['source']}" download>Download this notebook</a>
</section>
<nav class="lesson-nav" aria-label="Lesson navigation">
  {previous_link}
  {next_link}
</nav>
<footer class="site-footer">
  <p>Built from saved Jupyter notebook outputs. No notebook code runs in this website.</p>
</footer>
""".strip()


def render_notebook(lesson: dict[str, str], index: int, destination: Path) -> None:
    notebook_path = ROOT / "notebooks" / lesson["source"]
    notebook = nbformat.read(notebook_path, as_version=4)

    errors = [
        output
        for cell in notebook.cells
        if cell.cell_type == "code"
        for output in cell.get("outputs", [])
        if output.get("output_type") == "error"
    ]
    if errors:
        raise SystemExit(f"Refusing to publish {notebook_path.name}: it contains saved error output.")

    exporter = HTMLExporter(template_name="lab")
    exporter.exclude_input_prompt = True
    exporter.exclude_output_prompt = True
    exported, _ = exporter.from_notebook_node(
        notebook,
        resources={"metadata": {"name": lesson["title"]}},
    )

    page_title = f"{lesson['number']} · {lesson['title']} | Local-first assessment analysis"
    title_tag = f"<title>{html.escape(page_title)}</title>"
    if re.search(r"<title>.*?</title>", exported, flags=re.DOTALL | re.IGNORECASE):
        exported = re.sub(
            r"<title>.*?</title>",
            title_tag,
            exported,
            count=1,
            flags=re.DOTALL | re.IGNORECASE,
        )
    else:
        exported = exported.replace("</head>", f"{title_tag}\n</head>", 1)

    head = f"""
<meta name="description" content="{html.escape(lesson['description'], quote=True)}">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="../assets/site.css">
""".strip()
    exported = exported.replace("</head>", f"{head}\n</head>", 1)
    exported = re.sub(
        r"(<body(?:\s[^>]*)?>)",
        lambda match: f"{match.group(1)}\n{site_header('../')}",
        exported,
        count=1,
        flags=re.IGNORECASE,
    )
    exported = exported.replace("</body>", f"{lesson_footer(index)}\n</body>", 1)
    destination.write_text(exported, encoding="utf-8")


def lesson_cards() -> str:
    cards = []
    for lesson in LESSONS:
        cards.append(
            f"""
<li class="lesson-card">
  <a href="notebooks/{lesson['slug']}">
    <span class="lesson-card__number">{lesson['number']}</span>
    <span class="lesson-card__body">
      <strong>{html.escape(lesson['title'])}</strong>
      <span>{html.escape(lesson['description'])}</span>
    </span>
    <span class="lesson-card__arrow" aria-hidden="true">→</span>
  </a>
</li>
""".strip()
        )
    return "\n".join(cards)


def home_page() -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="A local-first Jupyter workshop for turning assessment exports into careful, research-grade explorations.">
  <title>Local, research-grade analysis of student assessment data</title>
  <link rel="stylesheet" href="assets/site.css">
</head>
<body class="landing-page">
  <a class="skip-link" href="#main-content">Skip to content</a>
  <header class="site-header" aria-label="Workshop header">
    <div class="site-header__inner">
      <a class="site-brand" href="index.html">
        <span class="site-brand__eyebrow">Local-first workshop</span>
        <span class="site-brand__name">Research-grade assessment analysis</span>
      </a>
      <nav class="site-nav" aria-label="Site navigation">
        <a href="#lessons">Lessons</a>
        <a href="#setup">Run locally</a>
        <a href="#downloads">Downloads</a>
      </nav>
    </div>
  </header>

  <main id="main-content">
    <section class="hero">
      <div class="hero__content">
        <p class="eyebrow">Jupyter notebooks · Python · synthetic data</p>
        <h1>Local, research-grade analysis of student assessment data</h1>
        <p class="hero__lede">Python running on your computer gives you private, professional-grade analysis. You do not need to know—or learn—Python to use it: an LLM can write, run, and revise the code while you guide the questions, review the work, and interpret the results. Your student data stays local.</p>
        <div class="button-row">
          <a class="button" href="notebooks/{LESSONS[0]['slug']}">Start the workshop</a>
          <a class="button button--secondary" href="downloads/data-analysis-workshop.zip" download>Download all files</a>
        </div>
      </div>
      <aside class="privacy-card" aria-label="Data handling note">
        <span class="privacy-card__icon" aria-hidden="true">◉</span>
        <div>
          <h2>Local by design</h2>
          <p>The notebooks make no network or AI calls. An AI assistant can help write generic code from a schema, but it never needs to see student records.</p>
        </div>
      </aside>
    </section>

    <section class="section" id="lessons">
      <div class="section-heading">
        <p class="eyebrow">Five-part sequence</p>
        <h2>Follow the analysis from question to presentation</h2>
        <p>The rendered lessons show saved results and require no setup. To edit or rerun the analysis, download the workshop and open the notebooks locally.</p>
      </div>
      <ol class="lesson-list">
        {lesson_cards()}
      </ol>
    </section>

    <section class="section section--tinted" id="setup">
      <div class="section-heading">
        <p class="eyebrow">Mac setup · no Python knowledge required</p>
        <h2>Ask your local agent to handle setup</h2>
        <p>The setup prompt directs an agent with local shell access to install JupyterLab Desktop, create an isolated environment with Seaborn, and make notebooks open with a double-click.</p>
      </div>
      <div class="setup-grid">
        <ol class="steps">
          <li><span>1</span><div><strong>Download and unzip the complete workshop</strong><p>Move it to a stable location before setup. Keep the notebooks, documentation, and synthetic CSV files together.</p></div></li>
          <li><span>2</span><div><strong>Open the Mac setup prompt</strong><p>It gives your agent explicit installation, privacy, verification, and future-library instructions.</p><p><a class="button button--small" href="setup-macos.html">View and copy the setup prompt</a></p></div></li>
          <li><span>3</span><div><strong>Paste it into your local agent</strong><p>The agent preflights Apple Command Line Tools, then uses Homebrew, JupyterLab Desktop, and a project-specific environment. Full Xcode is not required. You approve installation; the agent handles the commands.</p></div></li>
          <li><span>4</span><div><strong>Double-click the first notebook</strong><p>Open <code>notebooks/00_research_wow.ipynb</code> in Finder. Future libraries can be added by asking your agent in plain language.</p></div></li>
        </ol>
        <aside class="callout">
          <h3>Local setup, local data</h3>
          <p>Installing software requires network access, but setup does not require opening or transmitting assessment data. Analysis remains on your Mac.</p>
          <p>Local processing is not automatically policy-compliant. Use an approved device and follow your organization’s rules.</p>
          <p><strong>All data included here is synthetic.</strong></p>
        </aside>
      </div>
    </section>

    <section class="section" id="downloads">
      <div class="section-heading">
        <p class="eyebrow">Workshop files</p>
        <h2>Download the complete package or individual resources</h2>
      </div>
      <div class="download-grid">
        <a class="download-card download-card--featured" href="downloads/data-analysis-workshop.zip" download>
          <span class="download-card__type">ZIP</span>
          <strong>Complete workshop</strong>
          <span>Notebooks, synthetic data, setup instructions, and Python requirements</span>
        </a>
        <a class="download-card" href="downloads/FakeiReadyData.csv" download>
          <span class="download-card__type">CSV</span>
          <strong>Synthetic Reading data</strong>
          <span>Practice assessment export</span>
        </a>
        <a class="download-card" href="downloads/FakeiReadyMathData.csv" download>
          <span class="download-card__type">CSV</span>
          <strong>Synthetic Math data</strong>
          <span>Practice assessment export</span>
        </a>
        <a class="download-card" href="downloads/FakeiReadySchema.csv" download>
          <span class="download-card__type">CSV</span>
          <strong>Data schema</strong>
          <span>Field names and structure</span>
        </a>
        <a class="download-card" href="downloads/macos-setup-agent-prompt.md" download>
          <span class="download-card__type">PROMPT</span>
          <strong>Mac setup prompt</strong>
          <span>Instructions for a local agent</span>
        </a>
      </div>
    </section>
  </main>

  <footer class="site-footer site-footer--home">
    <p>Designed for assessment coordinators, research directors, program staff, and other domain experts learning to work with local data in Jupyter.</p>
  </footer>
</body>
</html>
"""


def macos_setup_page() -> str:
    prompt = html.escape(
        (ROOT / "prompts" / "macos-setup-agent-prompt.md").read_text(encoding="utf-8")
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="A copyable prompt for setting up the Jupyter workshop on macOS with a local agent.">
  <title>Mac setup prompt | Local-first assessment analysis</title>
  <link rel="stylesheet" href="assets/site.css">
</head>
<body class="prompt-page">
  {site_header("")}
  <main class="prompt-main" aria-labelledby="setup-title">
    <p class="eyebrow">Agent-assisted Mac setup</p>
    <h1 id="setup-title">Set up once. Double-click notebooks afterward.</h1>
    <p class="prompt-intro">Download and unzip the complete workshop first. Then paste the prompt below into a local agent that has permission to run shell commands on your Mac.</p>
    <div class="prompt-actions">
      <button class="button" id="copy-prompt" type="button">Copy setup prompt</button>
      <a class="button button--secondary" href="downloads/macos-setup-agent-prompt.md" download>Download prompt</a>
      <a class="text-link" href="index.html#setup">Back to setup overview</a>
    </div>
    <p class="copy-status" id="copy-status" role="status" aria-live="polite"></p>
    <section class="prompt-panel" aria-label="Mac setup prompt">
      <pre id="agent-prompt"><code>{prompt}</code></pre>
    </section>
    <aside class="callout prompt-note">
      <h2>What the agent will change</h2>
      <p>It first checks for Apple Command Line Tools and guides you through Apple’s installer if needed—full Xcode is not required. It then installs JupyterLab Desktop, <code>uv</code>, and <code>duti</code> through Homebrew; creates a private <code>.venv</code> inside the workshop; installs the recorded Python libraries; and associates <code>.ipynb</code> files with JupyterLab.</p>
      <p>The setup downloads software, but it does not need to read or transmit assessment records.</p>
    </aside>
  </main>
  <footer class="site-footer"><p>After setup, open the workshop by double-clicking <code>notebooks/00_research_wow.ipynb</code>.</p></footer>
  <script>
    const button = document.getElementById("copy-prompt");
    const prompt = document.getElementById("agent-prompt").innerText;
    const status = document.getElementById("copy-status");
    button.addEventListener("click", async () => {{
      try {{
        await navigator.clipboard.writeText(prompt);
        status.textContent = "Setup prompt copied.";
        button.textContent = "Copied";
      }} catch (error) {{
        status.textContent = "Copy was blocked by the browser. Select the prompt text below or use Download prompt.";
      }}
    }});
  </script>
</body>
</html>
"""


def copy_downloads(output: Path) -> None:
    downloads = output / "downloads"
    notebook_downloads = downloads / "notebooks"
    notebook_downloads.mkdir(parents=True, exist_ok=True)

    for filename in DATA_FILES:
        shutil.copy2(ROOT / filename, downloads / filename)
    shutil.copy2(
        ROOT / "prompts" / "macos-setup-agent-prompt.md",
        downloads / "macos-setup-agent-prompt.md",
    )
    for lesson in LESSONS:
        shutil.copy2(
            ROOT / "notebooks" / lesson["source"],
            notebook_downloads / lesson["source"],
        )

    archive_path = downloads / "data-analysis-workshop.zip"
    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in PACKAGE_FILES:
            archive.write(ROOT / relative, arcname=f"data-analysis-workshop/{relative}")


def validate_links(output: Path) -> None:
    missing: list[str] = []
    for page in output.rglob("*.html"):
        document = page.read_text(encoding="utf-8")
        for href in re.findall(r'href=["\']([^"\']+)["\']', document):
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc or href.startswith(("#", "mailto:")):
                continue
            target = (page.parent / unquote(parsed.path)).resolve()
            if not target.exists():
                missing.append(f"{page.relative_to(output)} -> {href}")
    if missing:
        formatted = "\n".join(f"- {link}" for link in missing)
        raise SystemExit(f"Built site contains missing local links:\n{formatted}")


def build(output: Path) -> None:
    require_sources()
    output = output.resolve()
    if output == ROOT or ROOT not in output.parents:
        raise SystemExit("Output must be a subdirectory of the workshop directory.")

    if output.exists():
        shutil.rmtree(output)
    (output / "assets").mkdir(parents=True)
    (output / "notebooks").mkdir(parents=True)

    shutil.copy2(ROOT / "assets" / "site.css", output / "assets" / "site.css")
    (output / ".nojekyll").write_text("", encoding="utf-8")
    (output / "index.html").write_text(home_page(), encoding="utf-8")
    (output / "setup-macos.html").write_text(macos_setup_page(), encoding="utf-8")

    for index, lesson in enumerate(LESSONS):
        render_notebook(lesson, index, output / "notebooks" / lesson["slug"])

    copy_downloads(output)
    validate_links(output)
    print(f"Built {len(LESSONS)} lessons and workshop downloads in {output}")


if __name__ == "__main__":
    build(parse_args().output)
