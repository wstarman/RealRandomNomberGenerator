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
        (rand_value, source_value) = await asyncio.to_thread(rng.getRand)

    return {
        'rand': rand_value,
        'source': source_value,
        'timestamp': datetime.now().isoformat()
    }


@app.get('/api/random', status_code=200)
async def api_random(response: Response) -> dict:
    try:
        return await asyncio.wait_for(random(), timeout=5)

    except Exception as e:
        if type(e) is asyncio.TimeoutError:
            logger.error("Request timed out after 5 seconds")
        else:
            logger.error(f"Error in api_random: {type(e).__name__}: {e}")
        traceback.print_exc()

        response.status_code = 500
        return {
            'error': 'Internal server error'
        }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
