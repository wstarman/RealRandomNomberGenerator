import asyncio
import threading
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import traceback

from RealRNG.RealRNG import RealRNG

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("FastAPI server starting")
    yield
    # Shutdown
    logger.info("Cleaning up RNG resources")
    rng.end()

app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4321",      # Astro frontend
        "http://127.0.0.1:4321",      # Astro frontend
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

rng = RealRNG()
rng_lock = threading.Lock()  # Serialize access to shared RNG instance

async def random():
    # Move blocking I/O to thread pool and protect with lock
    with rng_lock:
        rand_value = await asyncio.to_thread(rng.getRand)
        source_value = rng.getSource()  # Fast, no I/O

    return {
        'rand': rand_value,
        'source': source_value,
        'timestamp': datetime.now().isoformat()
    }


@app.get('/api/random', status_code=200)
async def api_random(response: Response) -> dict:
    try:
        return await asyncio.wait_for(random(), timeout=5)

    except asyncio.TimeoutError:
        logger.error("Request timed out after 5 seconds")
        response.status_code = 503
        return {
            'error': 'timeout',
            'message': 'Random number generation timed out',
            'source': 'fallback',
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error in api_random: {type(e).__name__}: {e}")
        traceback.print_exc()

        # Check if microphone is unavailable
        if rng.getSource() == rng.SOURCE_FALLBACK:
            response.status_code = 503
            return {
                'error': 'microphone_unavailable',
                'message': 'Microphone unavailable, using fallback',
                'source': 'fallback',
                'timestamp': datetime.now().isoformat()
            }
        else:
            response.status_code = 500
            return {
                'error': 'system_error',
                'message': 'Internal server error',
                'source': rng.getSource(),
                'timestamp': datetime.now().isoformat()
            }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
