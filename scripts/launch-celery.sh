celery -A eticketing_api worker -Q main_queue,notifications-queue -l INFO
celery -A eticketing_api beat -l INFO