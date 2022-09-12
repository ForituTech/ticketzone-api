release: chmod u+x scripts/release.sh && bash ./scripts/release.sh
web: gunicorn eticketing_api.wsgi
worker: celery -A eticketing_api worker -Q main_queue,notifications-queue
beat: celery -A eticketing_api beat