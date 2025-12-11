# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a lottery wheel application that generates truly random numbers using microphone input as an entropy source. The project consists of two main components:

1. **Python Backend** (`src/`): FastAPI server providing a random number generation API using the RealRNG library
2. **Frontend** (`lottery-wheel/`): Astro + React application with an interactive spinning wheel

## Environment Setup

### Prerequisites

- **Python 3.x** (tested with Python 3.13)
- **Node.js** and npm (for the Astro frontend)
- **System audio libraries** (for PyAudio)

### Backend Setup

1. **Install system dependencies for PyAudio**:

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-dev portaudio19-dev
   ```

   **Fedora:**
   ```bash
   sudo dnf install python3-devel portaudio-devel
   ```

   **macOS (via Homebrew):**
   ```bash
   brew install portaudio
   ```

2. **Install Python dependencies**:
   ```bash
   # From repository root
   pip install -r requirements.txt
   ```

   Note: PyAudio requires compilation, so `python3-dev` (or `python3-devel` on Fedora) is essential.

### Frontend Setup

```bash
# Navigate to frontend directory
cd lottery-wheel

# Install dependencies
npm install
```

## System Startup Process

The application requires **both backend and frontend** to run simultaneously for full functionality:

### Option 1: Manual Startup (Two Terminals)

**Terminal 1 - Backend:**
```bash
# From repository root
python src/server.py
# Server starts on http://127.0.0.1:8000
```

**Terminal 2 - Frontend:**
```bash
# From lottery-wheel directory
cd lottery-wheel
npm run dev
# Dev server starts on http://localhost:4321
```

### Option 2: Proxy Configuration (Recommended for Development)

Currently, the frontend makes requests to `/api/random` which will fail without a proxy to the backend. To fix this, add to `lottery-wheel/astro.config.mjs`:

```javascript
export default defineConfig({
  integrations: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000'
    }
  }
});
```

### Accessing the Application

- **Frontend UI**: http://localhost:4321
- **Backend API**: http://127.0.0.1:8000/api/random
- **API Docs**: http://127.0.0.1:8000/docs (FastAPI auto-generated)

## Architecture

### Backend (Python + FastAPI)

- **Location**: `src/`
- **Entry point**: `src/server.py`
- **RNG Library**: `src/RealRNG/RealRNG.py`

The RealRNG class generates random numbers by hashing microphone audio input (using PyAudio). If microphone access fails, it falls back to Python's standard random module.

- Primary endpoint: `GET /api/random` returns `{rand: float, source: string, timestamp: string}`
- The `source` field indicates whether "microphone" or "fallback" was used

### Frontend (Astro + React)

- **Location**: `lottery-wheel/`
- **Main page**: `lottery-wheel/src/pages/index.astro`
- **Interactive component**: `lottery-wheel/src/components/SpinWheel.jsx`

The SpinWheel component:
- Renders a spinning wheel with user-provided options (one per line)
- Attempts to fetch random numbers from `/api/random` backend endpoint
- Falls back to `Math.random()` if the API is unavailable
- Uses the random value to select a winner with visual spinning animation

## Development Commands

### Backend (Python)

Run from the repository root:

```bash
# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
python src/server.py
# Server runs on http://127.0.0.1:8000

# Test the RNG library directly
python src/RealRNG/RealRNG.py
# Includes selfTest() method that generates a matplotlib histogram of 10,000 samples
```

### Frontend (Astro)

Run from the `lottery-wheel/` directory:

```bash
# Install dependencies
npm install

# Start development server (localhost:4321)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Key Implementation Details

### RealRNG Library

- Uses PyAudio to capture 4 frames of microphone input
- Hashes the audio data with SHA-256 to produce a random number
- Returns float in range [0, 1)
- Automatically attempts to reconnect to microphone on each `getSource()` call if previously unavailable
- `selfTest()` method generates distribution histogram for validation

### Frontend-Backend Integration

The SpinWheel component expects the backend API to return:
```json
{
  "rand": 0.123456,    // float between 0 and 1
  "source": "microphone",
  "timestamp": "2024-01-01T12:00:00"
}
```

Note: The frontend currently checks `data.value` (line 54 in SpinWheel.jsx) but the backend returns `data.rand`. This is a known inconsistency.

### Color Assignment Algorithm

The `assignColors()` function in SpinWheel.jsx ensures:
- Adjacent wheel segments have different colors
- First and last segments have different colors (they're visually adjacent)
- Uses 4 preset colors cycling through the options

## Important Notes

- The Python backend requires microphone permissions to generate truly random numbers
- When microphone is unavailable, both frontend and backend have fallback mechanisms
- The wheel always spins 5 full rotations (1800°) plus the target angle for visual effect
- Wheel rotation is reset after spinning to avoid accumulating large transform values
- **Without proxy configuration**, the frontend will use `Math.random()` fallback since `/api/random` requests will fail
- PyAudio may require microphone permissions on first run; check system settings if the RNG falls back unexpectedly
