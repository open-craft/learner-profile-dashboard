from django.test import TestCase

from lpd.models import LearnerProfileDashboard


class LearnerProfileDashboardTests(TestCase):
    """LearnerProfileDashboard model tests."""

    def test_str(self):
        lpd = LearnerProfileDashboard(name='Empty LPD')
        self.assertEquals(str(lpd), 'Empty LPD')
