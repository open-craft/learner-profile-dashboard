# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lpd', '0005_collect_quantitative_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='intro_text',
            field=models.TextField(help_text=b'Introductory text to display below section title, and above questions belonging to this section (optional).', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='section',
            name='title',
            field=models.CharField(help_text=b'Text to display at the top of this section (optional).', max_length=120, null=True, blank=True),
        ),
    ]
