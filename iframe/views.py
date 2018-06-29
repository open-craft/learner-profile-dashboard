"""
Views for fixing iframe session termination in Safari.

This file and all related code is based on https://bitbucket.org/JackLeo/django-iframetoolbox.
"""

from django.shortcuts import render_to_response


def iframe_fix(request):
    """
    Allow user accessing page containing iframe in Safari to bootstrap a session.
    """
    return render_to_response('cookie_page.html')
