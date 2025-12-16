# Real Random Number Generator

A monorepo containing a real random number generator using audio input as an entropy source, with multiple frontend interfaces and a FastAPI backend.

## Project Overview

This project generates truly random numbers using microphone audio input as an entropy source. The system consists of a Python library (RealRNG), a FastAPI backend server, and two frontend interfaces.

## Monorepo Structure

```
RealRandomNomberGenerator/
├── src/
│   ├── RealRNG/              # Core random number generation library
│   │   ├── __init__.py
│   │   └── RealRNG.py        # Audio-based RNG implementation
│   └── server.py             # FastAPI backend server
│
├── basic-rng-ui/             # Simple Next.js frontend (Pages Router)
│   ├── components/           # React components
│   │   ├── RandomNumberDisplay.tsx
│   │   ├── RandomNumberDisplay.test.tsx
│   │   └── Welcome/
│   ├── pages/                # Next.js pages
│   ├── constants/            # Color constants
│   ├── test-utils/           # Testing utilities
│   ├── package.json
│   └── README.md             # Detailed frontend docs
│
├── lottery-wheel/            # Astro-based spinning wheel UI
│   ├── src/
│   │   ├── components/       # SpinWheel component
│   │   └── pages/
│   ├── package.json
│   └── README.md
│
├── tests/                    # Backend/library tests
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Components

### 1. RealRNG Library (`src/RealRNG/`)
- Audio-based random number generation
- Uses PyAudio to capture microphone input
- SHA-256 hashing for entropy extraction
- Device validation to prevent silent/muted devices
- Self-testing functionality

### 2. Backend Server (`src/server.py`)
- FastAPI REST API
- Endpoint: `GET /api/random`
- CORS enabled for localhost:3000 and localhost:8000
- 5-second timeout protection
- Error handling and logging

### 3. Basic RNG UI (`basic-rng-ui/`)
- Next.js 16 with Mantine UI
- Single-button interface
- Real-time status indicators
- Comprehensive test coverage (Jest + React Testing Library)
- Static export support

### 4. Lottery Wheel UI (`lottery-wheel/`)
- Astro + React
- Interactive spinning wheel visualization
- Visual feedback for random selection

## Prerequisites

- **Python 3.x** (for backend and library)
- **Node.js 18+** (for frontends)
- **npm** or **yarn** (for package management)
- **Microphone** (for audio entropy source)

## Installation

### 1. Install Python Dependencies

From the repository root:

```bash
pip install -r requirements.txt
```

#### Local Development with Virtual Environment (Recommended)

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install test dependencies
pip install pytest httpx

# Run backend tests
python3 -m pytest tests/ -v
```

Required packages:
- fastapi
- uvicorn
- PyAudio
- numpy
- matplotlib (optional, for visualization)

### 2. Install Basic RNG UI Dependencies

```bash
cd basic-rng-ui
npm install
cd ..
```

### 3. Install Lottery Wheel UI Dependencies

```bash
cd lottery-wheel
npm install
cd ..
```

## Startup Sequence

To run the full system, you need to start components in the following order:

### Step 1: Start the Backend Server

From the repository root:

```bash
python src/server.py
```

The server will start on `http://127.0.0.1:8000`

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Start a Frontend (Choose One)

#### Option A: Basic RNG UI (Recommended for simple usage)

In a new terminal:

```bash
cd basic-rng-ui
npm run dev
```

Access at: `http://localhost:3000`

#### Option B: Lottery Wheel UI

In a new terminal:

```bash
cd lottery-wheel
npm run dev
```

Access at: `http://localhost:4321` (default Astro port)

## Environment Configuration

### Basic RNG UI

Create `basic-rng-ui/.env.local` to customize the API URL:

```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Default value: `http://127.0.0.1:8000`

## Testing

### Backend/Library Tests

From the repository root:

```bash
python -m pytest tests/
```

The RealRNG library includes self-testing:
```python
from src.RealRNG.RealRNG import RealRNG
rng = RealRNG()
# Self-testing runs automatically during initialization
```

### Basic RNG UI Tests

```bash
cd basic-rng-ui
npm test
```

Test suite includes:
- Unit tests (7/7 passing)
- TypeScript type checking
- ESLint linting
- Prettier formatting
- Stylelint validation

Run specific test suites:
```bash
npm run jest          # Run Jest tests only
npm run typecheck     # TypeScript checking
npm run lint          # ESLint + Stylelint
npm run prettier:check # Code formatting check
```

### Lottery Wheel UI Tests

Currently no tests implemented.

## Development Workflow

This project follows **trunk-based development**:

1. Create short-lived feature branches from `main`
2. Make changes and test locally
3. Push to remote and create Pull Request
4. Get quick review and merge back to `main`
5. Keep `main` as the stable trunk

### Creating a Feature Branch

```bash
git checkout -b yourname/feat/feature-name
# Make changes
git add .
git commit -m "feat: description of changes"
git push origin yourname/feat/feature-name
```

### Merging Latest Changes

```bash
git checkout yourname/feat/feature-name
git merge main
# Resolve conflicts if any
git push origin yourname/feat/feature-name
```

## API Endpoints

### GET /api/random

Returns a random number with metadata.

**Response:**
```json
{
  "rand": 0.123456789,
  "source": "microphone",
  "timestamp": "2025-12-16T12:34:56.789012"
}
```

**Error Response (500):**
```json
{
  "error": "Internal server error"
}
```

## Troubleshooting

### Backend Issues

**Problem:** No audio input detected
- **Solution:** Ensure microphone is connected and not muted
- Check system audio settings
- Verify PyAudio installation

**Problem:** All random numbers are identical
- **Solution:** Device variance validation failed (silent/muted device)
- Check audio input levels
- Try a different microphone

### Frontend Issues

**Problem:** Network error when generating numbers
- **Solution:** Ensure backend is running on `http://127.0.0.1:8000`
- Check CORS configuration in `src/server.py`
- Verify `.env.local` settings

**Problem:** Tests failing with missing dependencies
- **Solution:** Run `npm install` to ensure all packages are installed
- Delete `node_modules` and `package-lock.json`, then reinstall

## Production Deployment

### Backend

```bash
uvicorn src.server:app --host 0.0.0.0 --port 8000
```

### Basic RNG UI (Static Export)

```bash
cd basic-rng-ui
npm run build
# Static files will be in basic-rng-ui/out/
```

Serve the `out/` directory with any static file server.

### Lottery Wheel UI

```bash
cd lottery-wheel
npm run build
# Static files will be in lottery-wheel/dist/
```

## License

See `basic-rng-ui/LICENCE` for licensing information.

## Contributors

- Backend & Library: Team
- Basic RNG UI: bywu
- Lottery Wheel UI: Team

## Additional Documentation

- Basic RNG UI details: `basic-rng-ui/README.md`
- Lottery Wheel UI details: `lottery-wheel/README.md`
