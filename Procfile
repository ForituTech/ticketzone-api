release: chmod u+x scripts/release.sh && bash ./scripts/release.sh
web: gunicorn eticketing_api.wsgi
worker: celery -A eticketing_api worker
beat: celery -A eticketing_api beat