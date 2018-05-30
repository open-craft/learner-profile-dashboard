# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lpd', '0008_help_text_updates'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='likertscalequestion',
            name='range_max_text',
        ),
        migrations.RemoveField(
            model_name='likertscalequestion',
            name='range_min_text',
        ),
        migrations.AlterField(
            model_name='likertscalequestion',
            name='answer_option_range',
            field=models.CharField(default=b'agreement', help_text=b'Range of values to display for answer options belonging to this question.', max_length=20, choices=[(b'agreement', b'agreement'), (b'value', b'value')]),
        ),
    ]
