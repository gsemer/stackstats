import logging
import uvicorn
import time
from fastapi import FastAPI, Request

from api.routes import router
from api.lifespan import lifespan


# Configure logging
logger = logging.getLogger("stackexchange_api")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s"
)


app = FastAPI(
    title="StackExchange API",
    description="API to retrieve data from StackExchange API and compute statistics",
    lifespan=lifespan
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    response.headers['X-Process-Time'] = f'{process_time:.4f}'

    logger.info(f"Request to {request.url.path} took {process_time:.4f}s")
    return response

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=5000, 
        reload=True, # set to False in production environment
        log_level="debug", 
        access_log=True
    )
