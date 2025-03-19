from async_fastapi_jwt_auth.exceptions import AuthJWTException  # type: ignore
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from routes import content

app = FastAPI(
    title="Content Mock API",
    description="Provide dummy content data.",
    version="1.0.0",
    docs_url="/api/openapi/",
    openapi_url="/api/openapi/api.json",
)
app.include_router(content, prefix="/api/v1/dummy")


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
