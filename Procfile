release: chmod u+x scripts/release.sh && bash ./scripts/release.sh
web: gunicorn -w 1 -k uvicorn.workers.UvicornWorker eticketing_api.asgi:app
celery: chmod u+x scripts/launch-celery.sh && bash ./scripts/launch-celery.sh