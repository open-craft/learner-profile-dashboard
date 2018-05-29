# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lpd', '0007_add_question_framing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='likertscalequestion',
            name='framing_text',
            field=models.TextField(help_text=b'Introductory text to display below question text and above answer options and input fields belonging to this question (optional).', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='multiplechoicequestion',
            name='framing_text',
            field=models.TextField(help_text=b'Introductory text to display below question text and above answer options and input fields belonging to this question (optional).', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='qualitativequestion',
            name='framing_text',
            field=models.TextField(help_text=b'Introductory text to display below question text and above answer options and input fields belonging to this question (optional).', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='rankingquestion',
            name='framing_text',
            field=models.TextField(help_text=b'Introductory text to display below question text and above answer options and input fields belonging to this question (optional).', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='section',
            name='intro_text',
            field=models.TextField(help_text=b'Introductory text to display below section title and above questions belonging to this section (optional).', null=True, blank=True),
        ),
    ]
