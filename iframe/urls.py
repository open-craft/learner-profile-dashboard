# -*- coding: utf-8 -*-

"""
URLs for fixing iframe session termination in Safari.

This file and all related code is based on https://bitbucket.org/JackLeo/django-iframetoolbox.
"""
from django.conf.urls import url

from iframe import views


app_name = 'iframe'

urlpatterns = [
    url(r'iframefix/$', views.iframe_fix, name='iframe_fix'),
]
