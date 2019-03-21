# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lpd', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question_id', models.PositiveIntegerField()),
                ('option_text', models.TextField(help_text=b'Text to display for this answer option.')),
                ('allows_custom_input', models.BooleanField(help_text=b'Whether this option allows learners to specify custom input. For example, a quantitative question might include an "Other" option that allows learners to specify what that option represents. The LPD will render this as: Other: ______________.')),
                ('influences_recommendations', models.BooleanField(help_text=b'Whether answers to this answer option should be sent to the adaptive engine to tune recommendations.')),
            ],
        ),
        migrations.CreateModel(
            name='KnowledgeComponent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kc_id', models.CharField(help_text=b'String that LPD and adaptive engine use to uniquely identify this knowledge component.', max_length=50)),
                ('kc_name', models.CharField(help_text=b'Verbose name for this knowledge component.', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='LikertScaleQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('question_text', models.TextField(help_text=b'Text to display above answer options (if any) and input fields.')),
                ('notes', models.TextField(help_text=b'Author notes about this question (optional).', null=True, blank=True)),
                ('randomize_options', models.BooleanField(help_text=b'Whether to display answer options in random order on LPD.')),
                ('answer_option_range', models.PositiveIntegerField(help_text=b'Number of values that learners can choose from for each answer option. For example, to create 5-point scale, set this to 5.')),
                ('range_min_text', models.CharField(help_text=b'Meaning of lowest value of Likert scale. For example: "Not very valuable".', max_length=50)),
                ('range_max_text', models.CharField(help_text=b'Meaning of highest value of Likert scale. For example: "Extremely valuable."', max_length=50)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MultipleChoiceQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('question_text', models.TextField(help_text=b'Text to display above answer options (if any) and input fields.')),
                ('notes', models.TextField(help_text=b'Author notes about this question (optional).', null=True, blank=True)),
                ('randomize_options', models.BooleanField(help_text=b'Whether to display answer options in random order on LPD.')),
                ('max_options_to_select', models.PositiveIntegerField(help_text=b'Maximum number of answer options that learner is allowed to select for this question. Set this to 1 to create a multiple choice question. Set this to a value larger than one to create a multiple response question.')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QualitativeAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(help_text=b'Answer that the learner provided to the associated question.')),
                ('learner', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QualitativeQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('question_text', models.TextField(help_text=b'Text to display above answer options (if any) and input fields.')),
                ('notes', models.TextField(help_text=b'Author notes about this question (optional).', null=True, blank=True)),
                ('question_type', models.CharField(help_text=b'Whether this question requires learners to produce a short answer or an essay.', max_length=20, choices=[(b'short-answer', b'short answer'), (b'essay', b'essay')])),
                ('influences_group_membership', models.BooleanField(help_text=b'Whether answers to this question should be taken into account when calculating group membership for specific learners.')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QuantitativeAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.PositiveIntegerField(help_text=b'The value that the learner chose for the associated question.')),
                ('answer_option', models.ForeignKey(to='lpd.AnswerOption', on_delete=models.CASCADE)),
                ('learner', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RankingQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('question_text', models.TextField(help_text=b'Text to display above answer options (if any) and input fields.')),
                ('notes', models.TextField(help_text=b'Author notes about this question (optional).', null=True, blank=True)),
                ('randomize_options', models.BooleanField(help_text=b'Whether to display answer options in random order on LPD.')),
                ('number_of_options_to_rank', models.PositiveIntegerField(help_text=b'Number of answer options belonging to this question that learners are allowed to rank.')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField(help_text=b"The learner's score for the associated knowledge component.")),
                ('knowledge_component', models.OneToOneField(to='lpd.KnowledgeComponent', on_delete=models.CASCADE)),
                ('learner', models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('title', models.CharField(help_text=b'Text to display above questions belonging to this section (optional).', max_length=120, null=True, blank=True)),
                ('lpd', models.ForeignKey(to='lpd.LearnerProfileDashboard', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='rankingquestion',
            name='section',
            field=models.ForeignKey(to='lpd.Section', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='qualitativequestion',
            name='section',
            field=models.ForeignKey(to='lpd.Section', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='qualitativeanswer',
            name='question',
            field=models.ForeignKey(to='lpd.QualitativeQuestion', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='multiplechoicequestion',
            name='section',
            field=models.ForeignKey(to='lpd.Section', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='likertscalequestion',
            name='section',
            field=models.ForeignKey(to='lpd.Section', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='answeroption',
            name='knowledge_component',
            field=models.OneToOneField(null=True, blank=True, to='lpd.KnowledgeComponent', help_text=b'Knowledge component that this answer option is associated with.', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='answeroption',
            name='question_type',
            field=models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE),
        ),
    ]
