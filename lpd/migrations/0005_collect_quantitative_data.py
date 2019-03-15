# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('lpd', '0004_submit_answers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answeroption',
            name='knowledge_component',
            field=models.OneToOneField(related_name='answer_option', null=True, blank=True, to='lpd.KnowledgeComponent', help_text=b'Knowledge component that this answer option is associated with.', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='score',
            name='knowledge_component',
            field=models.ForeignKey(to='lpd.KnowledgeComponent', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='score',
            name='learner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
    ]
