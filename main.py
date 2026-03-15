import logging
import uvicorn
from fastapi import FastAPI

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
