import json
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, AsyncIterator

import uvicorn

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response
from loguru import logger as log
from psycopg import Connection

from app.config import settings
from app.db.database import db_conn, get_db_connection_pool
from app.db.enums import HTTPStatus

from app.users import user_routes
from app.tasks import task_routes
from app.projects import project_routes

def get_api() -> FastAPI:
    """Return the FastAPI app, configured for the environment.

    Add endpoint profiler or monitoring setup based on environment.
    """
    api = get_application()
    # TODO: add endpoint profiler to check for bottlenecks
    # TODO：monitoring service with sentry/open observer
    return api

async def lifespan(
    app: FastAPI,  # dead: disable
) -> AsyncIterator[None]:
    """FastAPI startup/shutdown event."""
    log.debug("Starting up FastAPI server.")

    # Create a pooled db connection and make available in lifespan state
    # https://asgi.readthedocs.io/en/latest/specs/lifespan.html#lifespan-state
    # NOTE to use within a request (this is wrapped in database.py already):
    # from typing import cast
    # db_pool = cast(AsyncConnectionPool, request.state.db_pool)
    # async with db_pool.connection() as conn:
    db_pool = get_db_connection_pool()
    await db_pool.open()

    yield {"db_pool": db_pool}

    # Shutdown events
    log.debug("Shutting down FastAPI server.")
    await db_pool.close()

def get_application() -> FastAPI:
    """Get the FastAPI app instance, with settings."""
    _app = FastAPI(
        title=settings.APP_NAME,
        description="service example",
        debug=settings.DEBUG,
        lifespan=lifespan,
        # NOTE REST APIs should not have trailing slashes
        redirect_slashes=False,
    )

    # Set custom logger
    _app.logger = get_logger()

    # _app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=settings.EXTRA_CORS_ORIGINS,
    #     allow_credentials=True,
    #     allow_methods=["*"],
    #     allow_headers=["*"],
    #     expose_headers=["Content-Disposition"],
    # )

    _app.include_router(user_routes.router)
    _app.include_router(task_routes.router)
    _app.include_router(project_routes.router)

    return _app

class InterceptHandler(logging.Handler):
    """Intercept python standard lib logging."""

    def emit(self, record):
        """Retrieve context where the logging call occurred.

        This happens to be in the 6th frame upward.
        """
        logger_opt = log.opt(depth=6, exception=record.exc_info)
        logger_opt.log(logging.getLevelName(record.levelno), record.getMessage())

def get_logger():
    """Override FastAPI logger with custom loguru."""
    # Hook all other loggers into ours
    logger_name_list = [name for name in logging.root.manager.loggerDict]
    for logger_name in logger_name_list:
        logging.getLogger(logger_name).setLevel(settings.LOG_LEVEL)
        logging.getLogger(logger_name).handlers = []
        if logger_name == "urllib3":
            # Don't hook urllib3, called on each OTEL trace
            continue
        if "." not in logger_name:
            logging.getLogger(logger_name).addHandler(InterceptHandler())

    log.remove()
    log.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} "
            "| {name}:{function}:{line} | {message}"
        ),
        enqueue=True,  # Run async / non-blocking
        colorize=True,
        backtrace=True,  # More detailed tracebacks
        catch=True,  # Prevent app crashes
    )

    # Only log to file in production
    if not settings.DEBUG:
        log.add(
            "/opt/logs/service_example.json",
            level=settings.LOG_LEVEL,
            enqueue=True,
            serialize=True,  # JSON format
            rotation="00:00",  # New file at midnight
            retention="10 days",
            # format=log_json_format, # JSON format func
        )

api = get_api()

@api.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,  # dead: disable
    exc: RequestValidationError,
):
    """Exception handler for more descriptive logging and traces."""
    status_code = 500
    errors = []
    for error in exc.errors():
        # TODO Handle this properly
        if error["msg"] in ["Invalid input", "field required"]:
            status_code = HTTPStatus.UNPROCESSABLE_ENTITY
        else:
            status_code = HTTPStatus.BAD_REQUEST
        errors.append(
            {
                "loc": error["loc"],
                "msg": error["msg"],
                "error": error["msg"] + str([x for x in error["loc"]]),
            }
        )
    return JSONResponse(status_code=status_code, content={"errors": errors})


@api.get("/")
async def home():
    """Redirect home to docs."""
    return RedirectResponse("/docs")


@api.get("/__version__")
async def deployment_details():
    """Mozilla Dockerflow Spec: source, version, commit, and link to CI build."""
    details = {}

    version_path = Path("/opt/version.json")
    if version_path.exists():
        with open(version_path) as version_file:
            details = json.load(version_file)
    commit = details.get("commit", "commit key was not found in file!")
    build = details.get("build", "build key was not found in file!")

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content={
            "source": "https://github.com/necloud/service-example",
            "version": "0.0.1",
            "commit": commit or "/app/version.json not found",
            "build": build or "/app/version.json not found",
        },
    )

@api.get("/__heartbeat__")
async def heartbeat_plus_db(db: Annotated[Connection, Depends(db_conn)]):
    """Heartbeat that checks that API and DB are both up and running."""
    try:
        async with db.cursor() as cur:
            await cur.execute("SELECT 1")
        return Response(status_code=HTTPStatus.OK)
    except Exception as e:
        log.warning(e)
        log.warning("Server failed __heartbeat__ database connection check")
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"error": str(e)}
        )

@api.get("/__lbheartbeat__")
async def simple_heartbeat():
    """Simple ping/pong API response."""
    return Response(status_code=HTTPStatus.OK)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:api",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,  # Enable reload only in debug mode
        reload_dirs=["app"] if settings.DEBUG else None,  # Watch app dir only in debug
        log_level="debug" if settings.DEBUG else "info"
    )

