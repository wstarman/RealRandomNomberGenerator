# Round 1 Implementation Summary

## Quick Reference: What, Why, How, Where

### Step 1: CI + Python Linting

| Aspect | Details |
|--------|---------|
| **What** | GitHub Actions CI pipeline + Python linting config |
| **Why** | Ch1: Catch issues early (shift-left), Ch8: Automated style enforcement, Ch16: CI as quality gate before merge |
| **How** | CI triggers on push/PR, runs pytest + flake8 for Python, npm test for frontends |
| **Where** | `.github/workflows/ci.yml`, `pyproject.toml`, `.nvmrc`, `.python-version` |

**Files Created:**
```
.github/
└── workflows/
    └── ci.yml              # 146 lines - 3 jobs: backend, frontend-basic, frontend-lottery + integration
pyproject.toml              # 6 lines - Black + Flake8 config (100 char line length)
.nvmrc                      # 1 line - "18" (Node version)
.python-version             # 1 line - "3.13" (Python version)
```

---

### Step 2: Backend Unit Tests

| Aspect | Details |
|--------|---------|
| **What** | Pytest unit tests for FastAPI API and RealRNG library |
| **Why** | Ch1: "Beyonce Rule" - if you liked it, put a test on it, Ch11-12: Unit testing catches bugs early |
| **How** | MockRealRNG simulates audio hardware, TestClient tests API endpoints |
| **Where** | `tests/` directory |

**Files Created:**
```
tests/
├── __init__.py             # 1 line - makes tests a Python package
├── conftest.py             # 85 lines - pytest fixtures, MockRealRNG class
├── test_api.py             # 151 lines - 11 tests for /api/random endpoint
└── test_rng.py             # 262 lines - 10 tests for RealRNG class
```

**Test Coverage:**
- `test_api.py`: Response structure, status codes, field types, value ranges, error handling, CORS
- `test_rng.py`: getRand() range, getSource() values, fallback mode, cleanup, context manager

---

### Step 3: Postman/Newman Integration Tests

| Aspect | Details |
|--------|---------|
| **What** | Postman collection for API testing + Newman CLI runner |
| **Why** | Ch11: Integration tests validate end-to-end flow, Ch14: Larger testing for component interaction |
| **How** | Newman runs Postman collection via CLI, integrated into CI |
| **Where** | `tests/postman/` directory |

**Files Created:**
```
tests/
└── postman/
    ├── rng-api.postman_collection.json   # 82 lines - API test collection
    └── run-newman.sh                      # 5 lines - Newman runner script
```

**Test Assertions:**
1. Status code is 200
2. `rand` is number between 0-1
3. `source` is "microphone" or "fallback"
4. `timestamp` is ISO 8601 format
5. Response time under 5000ms

---

## Commit History

```
4ebc777 test: add Postman/Newman integration tests for API
c58a7b9 test: add backend unit tests for API and RNG library
7621960 feat: add GitHub Actions CI and Python linting config
```

**Total: 11 files, +1,016 lines**

---

## How to Verify Locally

### Run Backend Tests
```bash
cd /home/programmer/Projects/ntust-2025-fall-SWE/worktrees/swe-enhancements
pip install pytest httpx
pytest tests/ -v
```

### Run Linting
```bash
pip install flake8 black
flake8 src/ --max-line-length=100
black --check src/
```

### Run Integration Tests
```bash
# Terminal 1: Start server
python src/server.py

# Terminal 2: Run Newman
npm install -g newman
./tests/postman/run-newman.sh
```

---

## SWE Book References

| Chapter | Principle Applied | Implementation |
|---------|------------------|----------------|
| Ch1 | Shift-left testing, "Beyonce Rule" | Unit tests, CI on every PR |
| Ch8 | Automated style enforcement | Flake8, Black, ESLint, Prettier |
| Ch11 | Testing overview, test pyramid | Unit tests + integration tests |
| Ch12 | Unit testing best practices | MockRealRNG, fixtures, isolated tests |
| Ch14 | Larger testing | Postman/Newman integration tests |
| Ch16 | CI as merge gate | GitHub Actions on PR |

---

## For Round 2 Documentation

This summary can be used as source material for:
- **SDS (Software Design Specification)**: Architecture, components, CI/CD design
- **STS (Software Test Specification)**: Test strategy, test cases, coverage
- **Refactoring Report**: Before/after comparison, SWE principles applied
