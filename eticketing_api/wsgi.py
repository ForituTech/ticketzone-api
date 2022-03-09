import os

from dj_static import Cling  # noqa
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eticketing_api.settings")

application = Cling(get_wsgi_application())
