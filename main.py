import logging
import uvicorn

from config import ApiConfig


api_config = ApiConfig()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        "api:app",
        host=api_config.host,
        port=api_config.port,
        reload=True,
        log_level="info"
    )
