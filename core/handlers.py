from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from starlette.requests import Request
from starlette.responses import JSONResponse

from core.exceptions import HttpErrorException, HttpErrorExceptionFA


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HttpErrorExceptionFA)
    async def http_error_exception_fa(
        _: Request, exc: HttpErrorExceptionFA
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(
                {
                    "error_code": exc.code.name,
                    "error_message": exc.code.value.format(exc.extra),
                }
            ),
        )

    @app.exception_handler(HttpErrorException)
    async def http_error_exception(_: Request, exc: HttpErrorException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(
                {
                    "error_code": exc.code.name,
                    "error_message": exc.code.value.format(exc.extra),
                }
            ),
        )
