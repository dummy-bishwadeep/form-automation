import uvicorn
from fastapi import FastAPI
from scripts import services
from scripts.config import Services
from scripts.logging.logger import logger

app = FastAPI()
app.include_router(services.router)


# starting the application
if __name__ == "__main__":
    try:
        uvicorn.run("main:app", host=Services.HOST, port=Services.PORT, reload=True)
    except Exception as e:
        logger.exception(e)
