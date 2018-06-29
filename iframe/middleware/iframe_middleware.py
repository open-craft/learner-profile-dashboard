"""
Middleware for fixing iframe session termination in Safari.

This file and all related code is based on https://bitbucket.org/JackLeo/django-iframetoolbox.
"""
import logging

from django.shortcuts import render_to_response
from django.conf import settings


logger = logging.getLogger(__name__)

DEFAULT_P3P_POLICY = 'IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR IND CNT'
P3P_POLICY = getattr(settings, 'P3P_POLICY', DEFAULT_P3P_POLICY)


class IFrameFixMiddleware(object):
    """
    Middleware for fixing iframe session termination in Safari.
    """
    def process_request(self, request):  # pylint: disable=no-self-use,inconsistent-return-statements
        """
        Based on https://bitbucket.org/kmike/django-vkontakte-iframe/src/e6957bbdc5e3/vk_iframe/middleware.py

        Safari and Opera default security policies restrict cookie setting in first request in iframe.
        Solution is to create hidden form to preserve GET variables and REPOST it to current URL.

        Inspired by https://gist.github.com/796811 and https://gist.github.com/1511039.
        """
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        browser_is_safari = 'Safari' in user_agent and 'Chrome' not in user_agent
        first_request = 'cookie_fix' not in request.GET and request.COOKIES == {}

        if browser_is_safari and first_request:
            return render_to_response('cookie_warning.html')

    def process_response(self, request, response):  # pylint: disable=no-self-use
        """
        P3P policy for Internet Explorer.
        """
        response["P3P"] = 'CP="%s"' % P3P_POLICY
        return response
