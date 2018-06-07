# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lpd', '0009_likert_scale_labels'),
    ]

    operations = [
        migrations.AddField(
            model_name='answeroption',
            name='fallback_option',
            field=models.BooleanField(default=False, help_text=b'Whether this is a catch-all option that learners would choose if none of the other options apply to them.'),
        ),
    ]
