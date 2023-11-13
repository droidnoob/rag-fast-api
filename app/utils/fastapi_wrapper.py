from fastapi import FastAPI
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from app.utils.exceptions import ExceptionBase


class FastApiBuilder(object):
    def __init__(self, title, version, logger, env="LOCAL", **kwargs):
        """
        Initialize the FastApiBuilder instance.

        Args:
            title (str): The title of the FastAPI application.
            version (str): The version of the FastAPI application.
            logger: The logger instance for logging.
            env (str, optional): The environment mode. Defaults to "LOCAL".
            **kwargs: Additional keyword arguments for FastAPI configuration.
        """
        self.app = FastAPI(title=title, version=version, **self.config(env), **kwargs)
        self.logger = logger

    @staticmethod
    def config(env):
        if env == "PRODUCTION":
            return dict(
                docs_url=None,  # Disable docs (Swagger UI)
                redoc_url=None,  # Disable redoc
            )
        return dict()

    def handle_exceptions(self):
        """
        Add custom exception handlers to the application.
        """

        # Exception handler for custom ExceptionBase
        @self.app.exception_handler(ExceptionBase)
        def handle_base_exceptions(request, e: ExceptionBase):
            self.logger.exception(msg=repr(e))
            return JSONResponse(
                {
                    "status_code": e.status_code,
                    "exception": e.__class__.__name__,
                    "message": e.detail,
                }
            )

        # Exception handler for RequestValidationError
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request, e):
            self.logger.exception(msg=repr(e))
            return await request_validation_exception_handler(request, e)

        # Exception handler for server error
        @self.app.exception_handler(500)
        def handle_server_error(request, e: ExceptionBase):
            self.logger.exception(msg=repr(e))
            return JSONResponse(
                {"status_code": 500, "message": "Internal Server Error"}
            )

        return self

    def add_health_endpoint(self):
        @self.app.get("/health", status_code=200)
        def health():
            return {"status": "success"}

        return self

    def add_cors_middleware(self, origins):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        return self

    def add_root_router(self, root_router, prefix="/api/v1"):
        self.app.include_router(root_router, prefix=prefix)
        return self

    def add_static_file_server(self):
        from pathlib import Path

        Path("./app/uploads").mkdir(parents=True, exist_ok=True)
        self.app.mount(
            "/uploads", StaticFiles(directory="./app/uploads"), name="static"
        )
        return self

    def build(self):
        """
        Build and return the FastAPI application instance.
        """
        return self.app
