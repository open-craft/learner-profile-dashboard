"""
Tests for API client that communicates with VPAL's Adaptive Engine
"""

import ddt
from django.test import override_settings, TestCase
from mock import patch

from lpd.client import AdaptiveEngineAPIClient
from lpd.models import Score
from lpd.tests.factories import KnowledgeComponentFactory
from lpd.tests.mixins import UserSetupMixin


# Classes

@ddt.ddt
class AdaptiveEngineAPIClientTests(UserSetupMixin, TestCase):
    """
    Tests for API client that communicates with VPAL's Adaptive Engine.
    """

    @ddt.data(
        (u'student', u'student'),
        (u'7wJN637PYRIpN4kkaW5CEg++', 'ef024deb7ecf611229378924696e4212'),
    )
    @ddt.unpack
    @override_settings(
        OPENEDX_INSTANCE_DOMAIN='test.instance.com',
        ADAPTIVE_ENGINE_URL='https://test-url.com',
        ADAPTIVE_ENGINE_TOKEN='test-token',
    )
    def test_send_learner_data_user_id(self, username, expected_user_id):
        """
        Test that `send_learner_data` behaves correctly w/r/t computing LTI user IDs
        to send to adaptive engine.
        """
        self.user.username = username
        self.user.save()

        scores = []

        expected_url = 'https://test-url.com/engine/api/mastery/learner'
        expected_headers = {'Authorization': 'Token test-token'}
        expected_guid = 'test.instance.com'
        expected_payload = {
            'learner': {
                'lti_user_id': expected_user_id,
                'tool_consumer_instance_guid': expected_guid
            },
            'masteries': {}
        }

        with patch('lpd.client.requests.post') as patched_post:
            AdaptiveEngineAPIClient.send_learner_data(self.user, scores)
            patched_post.assert_called_once_with(
                expected_url, headers=expected_headers, json=expected_payload
            )

    @override_settings(
        OPENEDX_INSTANCE_DOMAIN='test.instance.com',
        ADAPTIVE_ENGINE_URL='https://test-url.com',
        ADAPTIVE_ENGINE_TOKEN='test-token',
    )
    def test_send_learner_data_masteries(self):
        """
        Test that `send_learner_data` behaves correctly w/r/t computing 'masteries' vector
        to send to adaptive engine.
        """
        expected_user_id = u'student'
        self.user.username = expected_user_id
        self.user.save()

        knowledge_component1 = KnowledgeComponentFactory(kc_id='kc_id_1')
        knowledge_component2 = KnowledgeComponentFactory(kc_id='kc_id_2')

        score1 = Score.objects.create(
            knowledge_component=knowledge_component1,
            learner=self.user,
            value=0.23,
        )
        score2 = Score.objects.create(
            knowledge_component=knowledge_component2,
            learner=self.user,
            value=0.42,
        )

        scores = [score1, score2]

        expected_url = 'https://test-url.com/engine/api/mastery/learner'
        expected_headers = {'Authorization': 'Token test-token'}
        expected_guid = 'test.instance.com'
        expected_payload = {
            'learner': {
                'lti_user_id': expected_user_id,
                'tool_consumer_instance_guid': expected_guid
            },
            'masteries': {
                knowledge_component1.kc_id: 0.23,
                knowledge_component2.kc_id: 0.42,
            }
        }

        with patch('lpd.client.requests.post') as patched_post:
            AdaptiveEngineAPIClient.send_learner_data(self.user, scores)
            patched_post.assert_called_once_with(
                expected_url, headers=expected_headers, json=expected_payload
            )
