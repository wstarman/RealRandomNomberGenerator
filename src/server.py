import asyncio
from fastapi import FastAPI, Response
from datetime import datetime
import traceback

from RealRNG.RealRNG import RealRNG

app = FastAPI()
rng = RealRNG()

async def random():
    # await asyncio.sleep(10)
    # raise RuntimeError
    return {
        'rand': rng.getRand(),
        'source': rng.getSource(),
        'timestamp': datetime.now().isoformat()
    }


@app.get('/api/random', status_code=200)
async def api_random(response: Response) -> dict:
    try:
        return await asyncio.wait_for(random(), timeout=5)
    except Exception as e:
        traceback.print_exc()
        response.status_code = 500
        return {'error': 'Internal server error'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
