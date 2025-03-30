from app.main import api
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        api,
        host="0.0.0.0",
        port=8000,
        workers=1,
        log_level="info",
    )
