# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lpd', '0003_basic_ui'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quantitativeanswer',
            name='value',
            field=models.PositiveIntegerField(help_text=b'The value that the learner chose for the associated answer option. Note that if the answer option belongs to a multiple choice question, this field will be set to 1 if the learner selected the answer option, and to 0 if the learner did not select the answer option. For ranking and Likert scale questions, this field will be set to the value that the learner chose from the range of available values.'),
        ),
    ]
