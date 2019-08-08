"""
Management command for producing CSV file listing download statistics for PDF exports of different LPD instances.
"""

import csv

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from lpd import models
from lpd.client import AdaptiveEngineAPIClient


# Classes

class Command(BaseCommand):
    """
    Management command for producing CSV file listing download statistics
    for PDF exports of different LPD instances.
    """
    help = (
        'Management command for producing CSV file listing download statistics '
        'for PDF exports of different LPD instances.'
    )

    # pylint: disable=superfluous-parens,too-many-locals
    def handle(self, *args, **options):
        """
        Produce CSV file listing download statistics for PDF exports of different LPD instances.
        """
        header = [
            "LPD username",
            "LTI user ID",
            "LPD ID",
            "LPD name",
            "Total number of downloads",
            "Downloads requested at"
        ]
        rows = [header]

        for u in User.objects.iterator():  # pylint: disable=not-an-iterable
            lpd_username = u.username
            lti_user_id = AdaptiveEngineAPIClient._decompress_username(lpd_username)

            print('Collecting download stats for user {lpd_username} (LTI user ID: {lti_user_id})...'.format(
                lpd_username=lpd_username,
                lti_user_id=lti_user_id
            ))

            for lpd in models.LearnerProfileDashboard.objects.iterator():
                print('... and LPD {lpd}.'.format(lpd=lpd))

                lpd_exports = models.LPDExport.objects.filter(
                    requested_by=u, requested_for=lpd
                ).order_by('requested_at')

                total_downloads = lpd_exports.count()
                export_request_times = lpd_exports.values_list('requested_at', flat=True)
                downloads_requested_at = '\n'.join([
                    requested_at.strftime('%Y-%m-%d %H:%M:%S (%Z)') for requested_at in export_request_times
                ])

                row = [lpd_username, lti_user_id, lpd.id, lpd.name, total_downloads, downloads_requested_at]
                rows.append(row)

            print('DONE.')

        print('Writing results to CSV file...')

        with open('lpd_exports_report.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(rows)

        print('DONE.')
