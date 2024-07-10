from scripts.config import Services
from scripts.logging.logger import logger
import uvicorn
import argparse

__author__ = 'H115-925 MOHAMMED SHIBILI O, H115-924 ARJUN B'
__date__ = '15 Mar 2023'

ap = argparse.ArgumentParser()

if __name__ == "__main__":
    try:
        logger.info(f"****Starting {Services.PROJECT_NAME} ***")
        print(f"****************************Starting {Services.PROJECT_NAME}****************************")
        ap.add_argument(
            "--port",
            "-p",
            required=False,
            default=Services.PORT,
            help="Port to start the application.",
        )
        ap.add_argument(
            "--bind",
            "-b",
            required=False,
            default=Services.HOST,
            help="IF to start the application.",
        )
        ap.add_argument(
            "--workers",
            "-w",
            type=int,
            default=Services.WORKERS,
            help="Number of worker processes to use.",
        )
        arguments = vars(ap.parse_args())

        logger.info(f"App Starting at {arguments['bind']}:{arguments['port']} with {arguments['workers']} workers.")
        uvicorn.run(
            "main:app",
            host=arguments["bind"],
            port=int(arguments["port"]),
            workers=arguments["workers"]
        )
    except Exception as e:
        logger.error(f"Error from app - {e}")
