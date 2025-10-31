---
description: "Diagnose why Python tests in VS Code are stuck during discovery or execution"
mode: "agent"
---

# Diagnose: VS Code Python tests appear stuck

**Role**: You are Copilot investigating why Python tests in VS Code hang during discovery or execution.
**Objective**: Identify the choke point (discovery vs execution vs config), show the smallest reproducible command, and propose a minimal, ordered fix. Be terse and actionable.

## Inputs (fill or infer)

* **Workspace root**: `<auto>`
* **Interpreter path**: `<infer from VS Code selection>`
* **Test framework**: `pytest | unittest | nose` (prefer `pytest` if present)
* **Primary tests dir(s)**: `tests` (and others if found)
* **Monorepo?**: `<detect multiple workspaces>`
* **OS / shell**: `<auto>`

## What to collect (automate where possible)

1. **VS Code Python Test Log** (most recent run) and full test command it issued.
2. **`.vscode/settings.json`** (effective testing entries).
3. **`pytest.ini` / `pyproject.toml` / `tox.ini`** relevant sections.
4. **`requirements*.txt` / `poetry.lock` / `pipfile.lock`** indicators for `pytest`, `pytest-asyncio`, etc.
5. **Interpreter** (`sys.executable`, `python -V`) and whether it matches VS Code’s selected interpreter.
6. **Last lines of** `python -m pytest --collect-only -vv` (or `python -m unittest discover -v`) until the stall.
7. **Extensions** likely to interfere (GitHub Copilot, Copilot Chat, Python, Python Debugger).

## Triage plan (run in order; stop when you find the cause)

### 0) Confirm it’s VS Code vs the suite

Run in the workspace root, using the same interpreter VS Code shows in the status bar:

```bash
python -m pytest -q
python -m pytest --collect-only -vv
# or:
python -m unittest discover -v
```

* **CLI hangs** ➜ it’s the suite/imports/fixtures.
* **CLI is fine, VS Code hangs** ➜ it’s config/extension/integration.

### 1) Surface the exact VS Code command

From the **Python Test Log**, copy the full command VS Code executed. Re-run it in the terminal verbatim. Note any divergence from Step 0.

### 2) Normalize VS Code testing config

Apply a minimal, predictable baseline (only if using pytest):

```jsonc
// .vscode/settings.json
{
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": ["-q", "--maxfail=1", "tests"],
  "python.testing.autoTestDiscoverOnSaveEnabled": false,
  "python.testing.logLevel": "Trace",
  "python.defaultInterpreterPath": "<abs path to venv python>"
}
```

Ensure a root `pytest.ini` exists:

```ini
# pytest.ini
[pytest]
testpaths = tests
addopts = -q --maxfail=1
markers =
    slow: long-running tests
    e2e: end-to-end tests
```

Re-discover tests and retry.

### 3) Find discovery blockers

Run and watch where it stops:

```bash
python -m pytest --collect-only -vv
```

Common offenders (inspect the last collected node and its imports):

* **Module-level side effects** (I/O, sleeps, network). Guard with:

  ```python
  if __name__ == "__main__":
      main()
  ```
* **Circular/missing imports** → fix import paths / install deps.
* **Autouse fixtures** doing heavy setup → remove `autouse=True`, narrow scope, or mark `@pytest.mark.slow`.
* **Async tests** without policy → install `pytest-asyncio`; add `asyncio_mode = auto` in `pytest.ini`.
* **Hidden `input()`** / stdin waits → remove or guard with env checks.

### 4) Cache/interpreter sanity pass

```bash
# Keep your active venv; replace .venv below if needed
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
rm -rf .pytest_cache
python -m pip install -U pip pytest pytest-asyncio
python -c "import sys; print(sys.executable); import platform; print(platform.platform())"
```

Ensure the printed interpreter matches VS Code’s selected one.

### 5) Extension interference A/B

Temporarily disable **GitHub Copilot** and **Copilot Chat**. Re-run discovery.
If behavior changes, keep Copilot enabled but leave **Auto Test Discovery** off and run tests manually.

### 6) Monorepo/workspace-folder edge cases

If multiple folders are present, ensure each has its own `pytest.ini` or configure per-folder `.vscode/settings.json` with `"python.testing.cwd"` and correct `pytestArgs`.

### 7) Re-run with minimal scope

```bash
python -m pytest -q -k "not slow and not e2e" tests
```

If this passes, mark heavy tests accordingly and reintroduce gradually.

## Decision & Fix table (fill these)

* **Root cause**: `<discovery | execution | config | extension | env | other>`
* **Culprit file/test**: `<path::test>`
* **Exact failing/hanging step**: `<command or import chain>`
* **One-line repro**: `<paste minimal pytest/unittest command>`
* **Minimal fix**: `<code/config change>`
* **Follow-up hardening**:

  * Keep side effects under `if __name__ == "__main__":`.
  * Add `pytest.ini` with `testpaths`, `addopts`, and markers.
  * Pin `pytest` and plugins; document local run commands.
  * Keep **Auto Test Discovery** off in large repos.

## Ready-to-run commands (Copilot: execute in integrated terminal)

```bash
# 1) Show pytest version and plugins
python -m pytest --version

# 2) Collect-only verbose to find exact stall point
python -m pytest --collect-only -vv

# 3) Print last 100 lines of Python Test Log if available
# (Copilot: read VS Code “Python Test Log” output channel)

# 4) Reproduce the exact VS Code command (paste from log)
<PASTE_COMMAND_FROM_TEST_LOG>

# 5) Quick env & interpreter confirmation
python -c "import sys,platform,site; print(sys.executable); print(platform.python_version()); print(site.getsitepackages())"
```

## Standard fix snippets

**Guard module-level code**

```python
def main():
    ...

if __name__ == "__main__":
    main()
```

**Async tests policy**

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
```

**Mark heavy tests**

```python
import pytest

@pytest.mark.slow
def test_big_download():
    ...
```

**Minimal VS Code settings**

```jsonc
{
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": ["-q", "--maxfail=1", "tests"],
  "python.testing.autoTestDiscoverOnSaveEnabled": false
}
```

## Output format (what you should return)

* **Diagnosis summary** (2–4 sentences).
* **Repro command** (single line).
* **Concrete fix** (code/config diff if applicable).
* **Why this works** (1–2 sentences).
* **Optional**: a short “next time” checklist.

---

**Stop once** you have a concrete repro and a minimal fix. Avoid broad refactors. If multiple causes exist, report the first blocker with a crisp fix, then note any secondary risks.
