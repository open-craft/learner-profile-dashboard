"""
API client for communicating with VPAL's Adaptive Engine
"""

import urlparse

from django.conf import settings
import requests


# Classes

class AdaptiveEngineAPIClient(object):
    """
    API client that handles communication with an instance of VPAL's Adaptive Engine.
    """

    @classmethod
    def send_learner_data(cls, user, scores):
        """
        Sends POST request with up-to-date learner data for `user` to adaptive engine.

        Endpoint: /engine/api/mastery/learner

        Example payload:

        {
            'learner': {
                'lti_user_id': <lti_user_id>,
                'tool_consumer_instance_guid': <instance_id>
            },
            'masteries': {
                '<kc_id_1>': <value>,
                '<kc_id_2>': <value>
            }
        }
        """
        url = urlparse.urljoin(settings.ADAPTIVE_ENGINE_URL, '/engine/api/mastery/learner')
        headers = {
            'Authorization': 'Token {}'.format(settings.ADAPTIVE_ENGINE_TOKEN)
        }
        payload = {
            'learner': {
                'lti_user_id': user.username,
                'tool_consumer_instance_guid': settings.OPENEDX_INSTANCE_DOMAIN,
            },
            'masteries': {},
        }
        for score in scores:
            payload['masteries'][score.knowledge_component.kc_id] = score.value
        requests.post(url, headers=headers, json=payload)
