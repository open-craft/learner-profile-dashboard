# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lpd', '0002_data_model'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answeroption',
            options={'ordering': ['-option_text']},
        ),
        migrations.AlterModelOptions(
            name='likertscalequestion',
            options={},
        ),
        migrations.AlterModelOptions(
            name='multiplechoicequestion',
            options={},
        ),
        migrations.AlterModelOptions(
            name='qualitativequestion',
            options={},
        ),
        migrations.AlterModelOptions(
            name='rankingquestion',
            options={},
        ),
        migrations.RenameField(
            model_name='answeroption',
            old_name='question_type',
            new_name='content_type',
        ),
        migrations.RenameField(
            model_name='answeroption',
            old_name='question_id',
            new_name='object_id',
        ),
        migrations.RemoveField(
            model_name='likertscalequestion',
            name='order',
        ),
        migrations.RemoveField(
            model_name='multiplechoicequestion',
            name='order',
        ),
        migrations.RemoveField(
            model_name='qualitativequestion',
            name='order',
        ),
        migrations.RemoveField(
            model_name='rankingquestion',
            name='order',
        ),
        migrations.AddField(
            model_name='likertscalequestion',
            name='number',
            field=models.PositiveIntegerField(default=1, help_text=b'Number of this question relative to parent section.'),
        ),
        migrations.AddField(
            model_name='multiplechoicequestion',
            name='number',
            field=models.PositiveIntegerField(default=1, help_text=b'Number of this question relative to parent section.'),
        ),
        migrations.AddField(
            model_name='qualitativequestion',
            name='number',
            field=models.PositiveIntegerField(default=1, help_text=b'Number of this question relative to parent section.'),
        ),
        migrations.AddField(
            model_name='quantitativeanswer',
            name='custom_input',
            field=models.CharField(help_text=b'The input that a learner provided for a quantitative question that `allows_custom_input`.', max_length=120, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='rankingquestion',
            name='number',
            field=models.PositiveIntegerField(default=1, help_text=b'Number of this question relative to parent section.'),
        ),
        migrations.AlterField(
            model_name='answeroption',
            name='allows_custom_input',
            field=models.BooleanField(default=False, help_text=b'Whether this option allows learners to specify custom input. For example, a quantitative question might include an "Other" option that allows learners to specify what that option represents. The LPD will render this as: Other: ______________.'),
        ),
        migrations.AlterField(
            model_name='answeroption',
            name='influences_recommendations',
            field=models.BooleanField(default=False, help_text=b'Whether answers to this answer option should be sent to the adaptive engine to tune recommendations.'),
        ),
        migrations.AlterField(
            model_name='likertscalequestion',
            name='answer_option_range',
            field=models.PositiveIntegerField(default=5, help_text=b'Number of values that learners can choose from for each answer option. For example, to create 5-point scale, set this to 5.'),
        ),
        migrations.AlterField(
            model_name='likertscalequestion',
            name='randomize_options',
            field=models.BooleanField(default=False, help_text=b'Whether to display answer options in random order on LPD.'),
        ),
        migrations.AlterField(
            model_name='likertscalequestion',
            name='range_max_text',
            field=models.CharField(default=b'strongly agree', help_text=b'Meaning of highest value of Likert scale. For example: "Extremely valuable."', max_length=50),
        ),
        migrations.AlterField(
            model_name='likertscalequestion',
            name='range_min_text',
            field=models.CharField(default=b'strongly disagree', help_text=b'Meaning of lowest value of Likert scale. For example: "Not very valuable".', max_length=50),
        ),
        migrations.AlterField(
            model_name='multiplechoicequestion',
            name='max_options_to_select',
            field=models.PositiveIntegerField(default=1, help_text=b'Maximum number of answer options that learner is allowed to select for this question. Set this to 1 to create a multiple choice question. Set this to a value larger than one to create a multiple response question.'),
        ),
        migrations.AlterField(
            model_name='multiplechoicequestion',
            name='randomize_options',
            field=models.BooleanField(default=False, help_text=b'Whether to display answer options in random order on LPD.'),
        ),
        migrations.AlterField(
            model_name='qualitativeanswer',
            name='question',
            field=models.ForeignKey(related_name='learner_answers', to='lpd.QualitativeQuestion', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='qualitativequestion',
            name='influences_group_membership',
            field=models.BooleanField(default=False, help_text=b'Whether answers to this question should be taken into account when calculating group membership for specific learners.'),
        ),
        migrations.AlterField(
            model_name='quantitativeanswer',
            name='answer_option',
            field=models.ForeignKey(related_name='learner_answers', to='lpd.AnswerOption', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='rankingquestion',
            name='number_of_options_to_rank',
            field=models.PositiveIntegerField(default=3, help_text=b'Number of answer options belonging to this question that learners are allowed to rank.'),
        ),
        migrations.AlterField(
            model_name='rankingquestion',
            name='randomize_options',
            field=models.BooleanField(default=False, help_text=b'Whether to display answer options in random order on LPD.'),
        ),
        migrations.AlterField(
            model_name='section',
            name='lpd',
            field=models.ForeignKey(related_name='sections', to='lpd.LearnerProfileDashboard', on_delete=models.CASCADE),
        ),
    ]
