release: chmod u+x scripts/release.sh && bash ./scripts/release.sh
web: gunicorn eticketing_api.wsgi
worker: celery -A urlshortener worker
beat: celery -A urlshortener beat