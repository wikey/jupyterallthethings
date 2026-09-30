Set up this Jupyter workshop on my Mac so that I can open its `.ipynb` files by double-clicking them in Finder. I should not need to know Python or run Terminal commands myself.

You are operating locally on my computer. Do not upload or transmit any workshop file, CSV content, notebook output, filename containing a person’s identity, or student information to an LLM, API, website, or other remote service. Installing trusted software and Python packages will require network access, but assessment data must remain local. Do not inspect CSV rows during setup.

Please do the following:

1. Locate the unzipped workshop directory. It contains `AGENTS.md`, `requirements.txt`, `scripts/setup_macos.sh`, and `notebooks/00_research_wow.ipynb`. If you cannot identify exactly one directory without broadly searching my files, ask me where I saved it.
2. Read `AGENTS.md` and `docs/agent-environment-guide.md` completely and follow them. Treat those files as the authoritative setup and future environment-maintenance instructions.
3. Confirm that this is macOS 12 or newer and that you have permission to execute local shell commands. If not, stop and clearly explain what is unavailable.
4. Check whether Homebrew is installed. If it is missing, explain that you need it to install JupyterLab Desktop and supporting tools, then ask for my approval before using the official installer from `https://brew.sh/`. Do not use an unofficial installer.
5. Review `scripts/setup_macos.sh`, summarize the local changes it will make, and run it from the workshop root. It should:
   - install the Homebrew cask `jupyterlab-app`, not the `jupyterlab` formula;
   - install `uv` and `duti`;
   - create or update the project-local `.venv` from `requirements.txt`, including Seaborn;
   - verify required imports without opening any data file;
   - configure JupyterLab Desktop to use `.venv/bin/python` for the `notebooks/` project directory;
   - associate `.ipynb` files with JupyterLab Desktop; and
   - open `notebooks/00_research_wow.ipynb` in JupyterLab Desktop.
6. Verify that JupyterLab Desktop’s project configuration points to this workshop’s `.venv/bin/python` and that macOS reports JupyterLab as the `.ipynb` handler. Do not claim success if either check fails.
7. If macOS asks me to approve opening JupyterLab or changing a file association, tell me exactly which button to click. Do not weaken Gatekeeper or other security controls.
8. When setup is complete, give me a short report containing:
   - whether double-click opening is ready;
   - the workshop folder you configured;
   - the Python environment path;
   - the installed JupyterLab, pandas, Matplotlib, and Seaborn versions;
   - how to start (`double-click notebooks/00_research_wow.ipynb`); and
   - a reminder that future library requests should be recorded in `requirements.txt`, installed into `.venv` with `uv`, verified without reading data, and followed by a notebook-kernel restart.

Do not install workshop packages globally, modify JupyterLab Desktop’s bundled Python environment, substitute a different notebook application, execute the analysis notebooks during setup, or move/delete any workshop data.
