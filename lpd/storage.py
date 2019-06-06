"""
Storage settings for LPD
"""

from django.conf import settings
from django.core.files.storage import default_storage
from storages.backends.s3boto3 import S3Boto3Storage


app_storage = None

if settings.USE_REMOTE_STORAGE:
    lpd_storage = S3Boto3Storage()
else:
    lpd_storage = default_storage


def export_path(instance, filename):
    """
    Return export path for LPD export represented by `instance`,
    taking into account desired `filename`.
    """
    return 'exports/lpd/{lpd_id}/learner/{username}/{filename}'.format(
        lpd_id=instance.requested_for.id,
        username=instance.requested_by.username,
        filename=filename
    )
