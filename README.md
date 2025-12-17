# Real Random Number Generator

A true random number generator using microphone audio as an entropy source.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontends                               │
│  ┌─────────────────────┐         ┌─────────────────────────┐    │
│  │   basic-rng-ui      │         │    lottery-wheel        │    │
│  │   (Next.js)         │         │    (Astro + React)      │    │
│  │   localhost:3000    │         │    localhost:4321       │    │
│  └──────────┬──────────┘         └───────────┬─────────────┘    │
└─────────────┼────────────────────────────────┼──────────────────┘
              │                                │
              ▼                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                        │
│                    localhost:8000                               │
│                    GET /api/random                              │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RealRNG Library                              │
│           Audio capture → SHA-256 hashing → Random float        │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 18+
- A microphone

### 1. Clone and Setup Backend

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
python src/server.py
```

The API will be available at `http://127.0.0.1:8000`

### 2. Start a Frontend

**Option A: Basic RNG UI** (simple button interface)
```bash
cd basic-rng-ui
npm install
npm run dev
```
Open `http://localhost:3000`

**Option B: Lottery Wheel** (spinning wheel visualization)
```bash
cd lottery-wheel
npm install
npm run dev
```
Open `http://localhost:4321`

## API

### GET /api/random

Returns a random number generated from microphone audio.

```json
{
  "rand": 0.7294618273,
  "source": "microphone",
  "timestamp": "2025-12-17T10:30:45.123456"
}
```

| Field | Description |
|-------|-------------|
| `rand` | Random float in range [0, 1) |
| `source` | `"microphone"` or `"fallback"` if mic unavailable |
| `timestamp` | ISO 8601 timestamp |

## Project Structure

```
RealRandomNomberGenerator/
├── src/
│   ├── RealRNG/          # Core random number library
│   └── server.py         # FastAPI backend
├── basic-rng-ui/         # Next.js frontend
├── lottery-wheel/        # Astro frontend
├── tests/                # Backend unit tests
└── .github/workflows/    # CI pipeline
```

## CI/CD

GitHub Actions runs on every pull request:

| Job | Description |
|-----|-------------|
| Backend | Python 3.13 unit tests |
| Frontend Basic | Next.js lint, typecheck, and Jest tests |
| Frontend Lottery | Astro build verification |
| Integration | Newman/Postman API tests against live server |

## Running Tests

**Backend:**
```bash
source .venv/bin/activate
python -m unittest tests/test_api_function.py -v
```

**Frontend (basic-rng-ui):**
```bash
cd basic-rng-ui
npm test
```

## Troubleshooting

**No audio input detected**
- Ensure microphone is connected and not muted
- Check system audio permissions

**Network error in frontend**
- Verify backend is running on `http://127.0.0.1:8000`
- Check browser console for CORS errors
