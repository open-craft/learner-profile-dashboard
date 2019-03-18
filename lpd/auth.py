"""
Custom logic for LTI integration
"""

import base64
import hashlib
import logging

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import IntegrityError

from django_lti_tool_provider import AbstractApplicationHookManager


logger = logging.getLogger(__name__)


class ApplicationHookManager(AbstractApplicationHookManager):
    """
    Class that performs authentication and redirection for LTI views.
    """

    LTI_KEYS = ['']

    @classmethod
    def _compress_username(cls, username):
        """
        Compress `username` and return it.

        Note that compression will only be applied if `username` is a normal edX hex user ID.
        Otherwise this method will return `username` unchanged.

        When changing the compression scheme that this method uses
        make sure to update `AdaptiveEngineAPIClient._decompress_username`,
        which reverts the compression scheme used here.
        """
        try:
            binary = username.decode('hex')
        except TypeError:
            # We didn't get a normal edX hex user ID, so we don't use our custom encoding.
            # This makes previewing questions in Studio work.
            return username
        else:
            return base64.urlsafe_b64encode(binary).replace('=', '+')

    @classmethod
    def _generate_password(cls, base, nonce):
        """
        Generate password for LTI user from `base` and `nonce`.
        """
        # It is totally fine to use md5 here, as it only generates PLAIN STRING password
        # which is then fed into secure password hash.
        generator = hashlib.md5()
        generator.update(base)
        generator.update(nonce)
        return generator.digest()

    def authenticated_redirect_to(self, request, lti_data):
        """
        Return redirect URL for authenticated LTI request.

        This method is abstract in the parent class, so we need to implement it here.
        """
        return reverse(settings.LTI_HOME_PAGE)

    def authentication_hook(self, request, user_id=None, username=None, email=None, extra_params=None):
        """
        Hook to authenticate user from data available in LTI request.

        This method is abstract in the parent class, so we need to implement it here.
        """
        # Automatically generate password from user_id.
        password = self._generate_password(user_id, settings.PASSWORD_GENERATOR_NONCE)

        # username and email might be empty, depending on how edX LTI module is configured:
        # There are individual settings for this module, and if it's embedded into an iframe
        # it never sends username and email in any case.
        # So, since we want to track user for both iframe and non-iframe LTI blocks, username is completely ignored.
        uname = self._compress_username(user_id)
        email = email if email else user_id+'@localhost'
        try:
            User.objects.get(username=uname)
        except User.DoesNotExist:
            try:
                User.objects.create_user(username=uname, email=email, password=password)
            except IntegrityError as e:
                # A result of race condition of multiple simultaneous LTI requests - should be safe to ignore,
                # as password and uname are stable (i.e. not change for the same user).
                logger.info("IntegrityError creating user - assuming result of race condition: %s", e.message)

        authenticated = authenticate(request, username=uname, password=password)
        login(request, authenticated)

    def vary_by_key(self, lti_data):
        return ":".join(str(lti_data.get(k, '')) for k in self.LTI_KEYS)
