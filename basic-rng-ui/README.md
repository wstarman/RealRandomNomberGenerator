# Basic Random Number Generator Interface

A minimalistic web interface for generating truly random numbers using the AudioRNG backend. Built with Next.js (Pages Router) and Mantine UI, following the SRS UI-001 and SDS Component 3 specifications.

## Overview

This interface provides a simple, user-friendly way to generate random numbers using the RealRNG library, which uses microphone audio input as an entropy source.

## Features

- Random number generation with visual feedback
- Status indicator showing entropy source (microphone or fallback)
- Loading overlay during API requests
- Error handling with user-friendly alerts
- Static export support for deployment as pure HTML/CSS/JS
- TypeScript for type safety
- Mantine UI component library
- Jest + React Testing Library for component tests
- Storybook for component development

## Prerequisites

- **Python 3.x** with dependencies installed (`pip install -r ../requirements.txt`)
- **Node.js** (version 18+)
- **npm** or **yarn**

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure API URL (optional):**

   The application is pre-configured to use `http://127.0.0.1:8000` as the backend API URL. If you need to change this, edit `.env.local`:
   ```bash
   NEXT_PUBLIC_API_URL=http://your-backend-url:port
   ```

## Running the Application

The application requires both the **backend** and **frontend** to run simultaneously.

### Terminal 1 - Backend (FastAPI)

From the repository root:
```bash
python src/server.py
```
The backend will start on **http://127.0.0.1:8000**

### Terminal 2 - Frontend (Next.js)

From this directory (`basic-rng-ui/`):
```bash
npm run dev
```
The frontend will start on **http://localhost:3000**

### Access the Application

Open your browser and navigate to:
- **Frontend UI:** http://localhost:3000
- **Backend API:** http://127.0.0.1:8000/api/random
- **API Docs:** http://127.0.0.1:8000/docs

## Building for Production

### Static Export (Recommended)

This application is configured for static export, generating pure HTML/CSS/JS files:

```bash
npm run build
```

This will create an `out/` directory containing the static files that can be deployed to any static hosting service.

**Note:** The static export makes direct API calls to the backend URL specified in `.env.local`. Make sure CORS is enabled on the backend.

## npm scripts

### Build and dev scripts

- `dev` – start dev server
- `build` – bundle application and export to static files
- `analyze` – analyzes application bundle with [@next/bundle-analyzer](https://www.npmjs.com/package/@next/bundle-analyzer)

### Testing scripts

- `typecheck` – checks TypeScript types
- `lint` – runs ESLint
- `prettier:check` – checks files with Prettier
- `jest` – runs jest tests
- `jest:watch` – starts jest watch
- `test` – runs `jest`, `prettier:check`, `lint` and `typecheck` scripts

### Other scripts

- `storybook` – starts storybook dev server on port 6006
- `storybook:build` – build production storybook bundle to `storybook-static`
- `prettier:write` – formats all files with Prettier

## Project Structure

```
basic-rng-ui/
├── components/
│   └── RandomNumberDisplay.tsx    # Main UI component
├── pages/
│   ├── _app.tsx                   # Mantine provider setup
│   ├── _document.tsx              # HTML document structure
│   └── index.tsx                  # Main page
├── .env.local                      # Environment variables (API URL)
├── next.config.mjs                 # Next.js configuration (static export)
└── package.json                    # Dependencies and scripts
```

## Key Components

### RandomNumberDisplay

The main component that handles:
- State management for random number, source, and timestamp
- API integration with environment-based URL
- Loading states and error handling
- UI rendering with Mantine components

**API Response Format:**
```json
{
  "rand": 0.123456789,
  "source": "microphone",
  "timestamp": "2025-12-11T10:30:00.123456"
}
```

## Troubleshooting

### Backend Connection Issues

If you see "Failed to generate random number" errors:
1. Ensure the backend server is running (`python src/server.py`)
2. Verify the backend is accessible at http://127.0.0.1:8000/api/random
3. Check that CORS is enabled in the backend for `http://localhost:3000`
4. Verify `.env.local` has the correct API URL

### Static Export Issues

If `npm run build` fails:
- Ensure all components are client-side compatible
- Check that no server-side Next.js features are used
- Verify `output: 'export'` is set in `next.config.mjs`

## Requirements Compliance

This implementation satisfies:
- **SRS UI-001**: Basic Random Number Generator Interface requirements
- **SDS Component 3**: Frontend Basic (WebUI) design specifications
- All functional requirements FR-005.1 through FR-005.7
- All UI requirements UI-001.1 through UI-001.5
