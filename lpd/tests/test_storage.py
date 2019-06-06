"""
Tests for functionality related to storing files.
"""

from django.test import TestCase

from lpd import storage
from lpd.tests import factories


# Classes

class StorageTests(TestCase):
    """
    Tests for functionality related to storing files.
    """

    def test_export_path(self):
        """
        Test that `export_path` returns appropriate upload path for PDF exports.
        """
        learner = factories.UserFactory(username='student_user')
        lpd = factories.LearnerProfileDashboardFactory(id=23)
        lpd_export = factories.LPDExportFactory(requested_by=learner, requested_for=lpd)
        filename = 'learner-profile.pdf'

        path = storage.export_path(lpd_export, filename)

        self.assertEqual(path, 'exports/lpd/23/learner/student_user/learner-profile.pdf')
