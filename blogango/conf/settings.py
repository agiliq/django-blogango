from django.conf import settings

AKISMET_API_KEY = getattr(settings, 'AKISMET_API_KEY', '')
AKISMET_COMMENT = bool(AKISMET_API_KEY)
