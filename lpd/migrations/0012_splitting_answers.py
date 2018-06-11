# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lpd', '0011_submissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='qualitativequestion',
            name='split_answer',
            field=models.BooleanField(default=False, help_text=b'Whether answers to this question consist of a comma-separated list of values that should be stored as separate answers to facilitate certain post-processing steps after export.'),
        ),
    ]
