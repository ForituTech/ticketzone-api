gunicorn -w 1 -k uvicorn.workers.UvicornWorker eticketing_api.asgi:app
celery -A eticketing_api beat -l INFO
