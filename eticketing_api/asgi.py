"""
ASGI config for eticketing_api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination

from core.handlers import register_exception_handlers
from eticketing_api import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eticketing_api.settings")
application = get_wsgi_application()

# This endpoint imports should be placed below the settings env declaration
# Otherwise, django will throw a configure() settings error
from eticketing_api.fastapi_router import router as api_router  # noqa


def get_application() -> FastAPI:
    # Main Fast API application
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"/{settings.OPEN_API_VERSION_STRING}/openapi.json",
        debug=settings.DEBUG,
    )

    # Set all CORS enabled origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    # Include all api endpoints
    app.include_router(api_router, prefix=f"/{settings.OPEN_API_VERSION_STRING}")

    # Set Up the static files and directory to serve django static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Mounts an independent web URL for DRF API
    app.mount("/", WSGIMiddleware(application))

    add_pagination(app)

    return app


app = get_application()
