"""
Middleware for timezone-related modifications.
"""

import pytz

from django.conf import settings
from django.utils import timezone


class TimezoneMiddleware(object):
    """
    Middleware for timezone-related modifications.
    """
    def process_request(self, request):  # pylint: disable=no-self-use
        """
        Update current timezone to match default timezone.
        """
        timezone.activate(pytz.timezone(settings.TIME_ZONE))
