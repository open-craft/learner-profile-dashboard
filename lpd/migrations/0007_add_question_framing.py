# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lpd', '0006_add_section_intro'),
    ]

    operations = [
        migrations.AddField(
            model_name='likertscalequestion',
            name='framing_text',
            field=models.TextField(help_text=b'Introductory text to display below question text, and above answer options and input fields belonging to this question (optional).', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='multiplechoicequestion',
            name='framing_text',
            field=models.TextField(help_text=b'Introductory text to display below question text, and above answer options and input fields belonging to this question (optional).', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='qualitativequestion',
            name='framing_text',
            field=models.TextField(help_text=b'Introductory text to display below question text, and above answer options and input fields belonging to this question (optional).', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='rankingquestion',
            name='framing_text',
            field=models.TextField(help_text=b'Introductory text to display below question text, and above answer options and input fields belonging to this question (optional).', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='likertscalequestion',
            name='question_text',
            field=models.TextField(help_text=b'Text to display above framing text, answer options (if any) and input fields.'),
        ),
        migrations.AlterField(
            model_name='multiplechoicequestion',
            name='question_text',
            field=models.TextField(help_text=b'Text to display above framing text, answer options (if any) and input fields.'),
        ),
        migrations.AlterField(
            model_name='qualitativequestion',
            name='question_text',
            field=models.TextField(help_text=b'Text to display above framing text, answer options (if any) and input fields.'),
        ),
        migrations.AlterField(
            model_name='rankingquestion',
            name='question_text',
            field=models.TextField(help_text=b'Text to display above framing text, answer options (if any) and input fields.'),
        ),
    ]
