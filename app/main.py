from app.resources import app_settings, get_elastic_client
from app.logger import logger
from app.routes import root_router
from app.utils.fastapi_wrapper import FastApiBuilder


allowed_origins = [
    "http://localhost",
    "http://localhost:8000",
]

app = (
    FastApiBuilder(
        title=app_settings.app_name,
        version=app_settings.version,
        logger=logger,
        env=app_settings.env,
    )
    .handle_exceptions()
    .add_cors_middleware(allowed_origins)
    .add_health_endpoint()
    .add_root_router(root_router)
    .add_static_file_server()
    .build()
)


@app.on_event("startup")
async def startup():
    logger.info("web server is up")
    if not get_elastic_client().ping():
        raise Exception("Unable to connect to Elastic Search")


@app.on_event("shutdown")
async def shutdown():
    logger.info("web server shutdown")
    get_elastic_client().close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
