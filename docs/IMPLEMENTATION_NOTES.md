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

## Step 2: Backend Unit Tests

### What was added

- `tests/__init__.py` - Makes tests directory a Python package
- `tests/conftest.py` - Pytest fixtures and MockRealRNG implementation
- `tests/test_api.py` - Unit tests for FastAPI endpoints
- `tests/test_rng.py` - Unit tests for RealRNG library

### Why (SWE principles)

**Chapter 1: What is Software Engineering?**
- "Beyonce Rule": If you liked it, put a test on it. Tests ensure code quality persists over time as the project evolves.
- Shift-left testing: Catching bugs early in development is cheaper and faster than finding them in production.
- Tests serve as executable documentation showing how the code is intended to be used.

**Chapter 11: Testing Overview**
- Unit tests verify individual components in isolation (API endpoints, RNG methods)
- Mocking external dependencies (PyAudio hardware) makes tests fast, reliable, and reproducible
- Tests validate both happy paths (successful operations) and error conditions (RNG failures, missing hardware)
- Comprehensive test coverage increases confidence when refactoring or adding new features

**Chapter 12: Unit Testing**
- Each test focuses on a single behavior or requirement
- Tests are independent and can run in any order
- Mock objects (MockRealRNG) replace real dependencies for predictable testing
- Tests verify contracts: return types, value ranges, error handling

### Test coverage

**test_api.py (11 tests):**
- Response structure and status codes (200 success, 500 error)
- Field validation (rand, source, timestamp present and correct types)
- Value constraints (rand between 0-1)
- Timestamp format validation (ISO format)
- Source field values (microphone/fallback)
- Error handling when RNG fails
- Multiple sequential requests (stateless verification)
- CORS middleware integration

**test_rng.py (10 tests):**
- getRand() returns float in [0, 1] range
- getSource() returns valid string ("microphone" or "fallback")
- Fallback mode when no audio device available
- Microphone mode when device present
- Multiple calls work consistently
- Resource cleanup (end() method)
- Context manager support (with statement)
- Source constants defined correctly

**conftest.py:**
- MockRealRNG class simulating hardware without requiring microphone
- Pytest fixtures for test client and mock RNG
- Configurable mock behavior (source type, failure simulation)

### How to run locally

```bash
cd /home/programmer/Projects/ntust-2025-fall-SWE/worktrees/swe-enhancements
pip install pytest httpx
pytest tests/ -v
```

**Run specific test files:**
```bash
pytest tests/test_api.py -v
pytest tests/test_rng.py -v
```

**Run with coverage report:**
```bash
pip install pytest-cov
pytest tests/ --cov=src --cov-report=term-missing
```

**Run tests in parallel (faster):**
```bash
pip install pytest-xdist
pytest tests/ -n auto
```
