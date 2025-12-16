# Implementation Notes

## Step 1: CI + Linting

### What was added

- `.github/workflows/ci.yml` - GitHub Actions CI workflow
- `pyproject.toml` - Python tooling configuration (Black, Flake8)
- `.nvmrc` - Node Version Manager configuration
- `.python-version` - Python version specification
- `docs/IMPLEMENTATION_NOTES.md` - This documentation file

### Why (SWE principles)

**Chapter 1: What is Software Engineering?**
- Software engineering is programming integrated over time. CI/CD and linting ensure code quality persists as the codebase evolves and multiple developers contribute.
- These tools help manage the "time dimension" of software by catching issues early and maintaining consistent standards.

**Chapter 8: Style Guides and Rules**
- Automated linting (Flake8, Black) enforces consistent code style across the project.
- Reduces friction in code reviews by automatically catching style violations.
- Tools like Black provide automatic formatting, eliminating debates about style preferences.
- Consistency improves readability and reduces cognitive load when switching between different parts of the codebase.

**Chapter 16: Version Control and Branch Management**
- CI runs on every push and pull request, providing rapid feedback on code changes.
- Automated testing in CI ensures that changes don't break existing functionality before merging.
- Branch protection can be configured to require passing CI checks before merging to main.
- This creates a safety net that scales as the team and codebase grow.

### How it works

**GitHub Actions CI Workflow:**
- Triggers automatically on pushes to main branch and all pull requests
- Runs three parallel jobs:
  1. **backend**: Sets up Python 3.13, installs dependencies, runs Flake8 linting, runs pytest (if tests exist)
  2. **frontend-basic**: Sets up Node 18, installs dependencies with npm ci, runs Jest tests
  3. **frontend-lottery**: Sets up Node 18, installs dependencies, runs production build

**Python Linting Configuration:**
- `pyproject.toml` configures Black (formatter) and Flake8 (linter) with 100-character line length
- Consistent line length across formatting and linting tools prevents conflicts
- Excludes common non-source directories (venv, __pycache__, .git)

**Version Management:**
- `.nvmrc` ensures consistent Node.js version (18) across development and CI
- `.python-version` specifies Python 3.13 for tools like pyenv and CI environments
- These files serve as single source of truth for runtime versions

### How to test locally

**Python linting:**
```bash
# Install linting tools
pip install flake8 black

# Run Flake8
flake8 src/

# Check formatting with Black (--check mode doesn't modify files)
black --check src/

# Auto-format with Black
black src/
```

**Frontend testing:**
```bash
# Basic Next.js UI
cd basic-rng-ui
npm ci
npm test

# Lottery wheel (build only, no tests yet)
cd lottery-wheel
npm ci
npm run build
```

**Full CI simulation:**
```bash
# From project root, run all checks in sequence
pip install -r requirements.txt
pip install pytest flake8 black
flake8 src/
pytest tests/ || echo "No tests directory"
cd basic-rng-ui && npm ci && npm test && cd ..
cd lottery-wheel && npm ci && npm run build && cd ..
```

**Verify version files:**
```bash
# Check Node version (with nvm)
nvm use
node --version  # Should be v18.x.x

# Check Python version (with pyenv)
pyenv local
python --version  # Should be 3.13.x
```
