# -*- coding: utf-8 -*-

"""
Top-level URLs for Learner Profile Dashboard
"""

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
    url(r'^iframe/', include('iframe.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^lti/', include('django_lti_tool_provider.urls')),
    url(r'^', include('lpd.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
