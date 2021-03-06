"""
API client for communicating with VPAL's Adaptive Engine
"""

import base64
import logging
import pprint
import urlparse

from django.conf import settings
import requests


# Globals

log = logging.getLogger(__name__)


# Classes

class AdaptiveEngineAPIClient(object):
    """
    API client that handles communication with an instance of VPAL's Adaptive Engine.
    """

    @classmethod
    def _decompress_username(cls, username):
        """
        Decompress `username` and return it.

        Reverts the compression scheme used by `ApplicationHookManager._compress_username`,
        so make sure to update that method when making changes here.

        Note that `username` is of type `unicode`, so we need to turn it into a `str`
        before reversing the compression scheme.
        """
        username_bytes = username.encode()
        try:
            binary = base64.urlsafe_b64decode(username_bytes.replace('+', '='))
        except TypeError:
            # Username does not use custom encoding from `ApplicationHookManager._compress_username`,
            # so return it unchanged.
            return username
        else:
            return binary.encode('hex')

    @classmethod
    def send_learner_data(cls, user, scores):
        """
        Sends PUT request with up-to-date learner data for `user` to adaptive engine.

        Endpoint: /engine/api/mastery/bulk_update

        Example payload:

        [
            {
                'knowledge_component': {
                    'kc_id': '<kc_id_1>'
                },
                'learner': {
                    'tool_consumer_instance_guid': settings.OPENEDX_INSTANCE_DOMAIN,
                    'user_id': '<lti_user_id>'
                },
                'value': 0.1
            },
            {
                'knowledge_component': {
                    'kc_id': '<kc_id_2>'
                },
                'learner': {
                    'tool_consumer_instance_guid': settings.OPENEDX_INSTANCE_DOMAIN,
                    'user_id': '<lti_user_id>'
                },
                'value': 0.3
            },
        ]
        """
        url = urlparse.urljoin(settings.ADAPTIVE_ENGINE_URL, '/engine/api/mastery/bulk_update')
        headers = {
            'Authorization': 'Token {}'.format(settings.ADAPTIVE_ENGINE_TOKEN)
        }
        learner_info = {
            'user_id': cls._decompress_username(user.username),
            'tool_consumer_instance_guid': settings.OPENEDX_INSTANCE_DOMAIN,
        }
        payload = []
        for score in scores:
            payload.append({
                'knowledge_component': {
                    'kc_id': score.knowledge_component.kc_id,
                },
                'learner': learner_info,
                'value':  score.value,
            })
        log.info(
            'Attempting to transmit the following payload to %s:\n%s',
            url,
            pprint.pformat(payload)
        )
        log.info(
            'Number of knowledge components in payload: %d',
            len(payload)
        )
        requests.put(url, headers=headers, json=payload)
