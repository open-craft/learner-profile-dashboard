# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lpd', '0010_introduce_fallback_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated', models.DateTimeField(help_text=b'The date and time at which the learner associated with this submission last submitted the section associated with this submission.', null=True, blank=True)),
                ('learner', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('section', models.ForeignKey(to='lpd.Section', on_delete=models.CASCADE)),
            ],
        ),
    ]
