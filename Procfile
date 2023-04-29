release: chmod u+x scripts/release.sh && bash ./scripts/release.sh
web: chmod u+x scripts/launch.sh && bash ./scripts/launch.sh
worker: celery -A eticketing_api worker -Q main_queue,notifications-queue -l INFO