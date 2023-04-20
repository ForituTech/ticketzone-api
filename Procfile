release: chmod u+x scripts/release.sh && bash ./scripts/release.sh
web: gunicorn -w 2 -k uvicorn.workers.UvicornWorker eticketing_api.asgi:app
worker: celery -A eticketing_api worker -Q main_queue,notifications-queue -l INFO
beat: celery -A eticketing_api beat -l INFO