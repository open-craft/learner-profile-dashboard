"""
Factories for Learner Profile Dashboard tests
"""

import random

from django.contrib.auth import get_user_model
import factory

from lpd.constants import QuestionTypes
from lpd import models


class UserFactory(factory.DjangoModelFactory):
    """Factory for users."""
    # This class was adapted from edx-platform/common/djangoapps/student/tests/factories.py.
    class Meta:
        model = get_user_model()
        django_get_or_create = ['username', 'email']

    username = factory.Sequence(u'robot{0}'.format)
    email = factory.Sequence(u'robot+test+{0}@edx.org'.format)
    password = factory.PostGenerationMethodCall('set_password', 'test')
    first_name = factory.Sequence(u'Robot{0}'.format)
    last_name = 'Test'
    is_staff = False
    is_active = True
    is_superuser = False


class LearnerProfileDashboardFactory(factory.DjangoModelFactory):
    """Factory for LPDs."""
    class Meta:
        model = models.LearnerProfileDashboard
        django_get_or_create = ['name']

    name = factory.Sequence(u'LPD {0}'.format)


class SectionFactory(factory.DjangoModelFactory):
    """Factory for sections."""
    class Meta:
        model = models.Section
        django_get_or_create = ['title']

    lpd = factory.SubFactory(LearnerProfileDashboardFactory)
    title = factory.Sequence(u'Section {0}'.format)
    order = factory.Sequence(lambda n: n)


class QuestionFactory(factory.DjangoModelFactory):
    """Factory for questions."""
    class Meta:
        django_get_or_create = ['number']

    section = factory.SubFactory(SectionFactory)
    number = factory.Sequence(lambda n: n)
    question_text = factory.Sequence(u'Is this question number {0}?'.format)
    notes = factory.Sequence(u'These are notes for question number {0}.'.format)


class QualitativeQuestionFactory(QuestionFactory):
    """Factory for qualitative questions."""
    class Meta:
        model = models.QualitativeQuestion

    question_type = random.choice(QuestionTypes.get_qualitative_types())


class MultipleChoiceQuestionFactory(QuestionFactory):
    """Factory for multiple choice questions."""
    class Meta:
        model = models.MultipleChoiceQuestion

    max_options_to_select = random.randint(1, 15)


class RankingQuestionFactory(QuestionFactory):
    """Factory for ranking questions."""
    class Meta:
        model = models.RankingQuestion

    number_of_options_to_rank = random.randint(1, 5)


class LikertScaleQuestionFactory(QuestionFactory):
    """Factory for Likert scale questions."""
    class Meta:
        model = models.LikertScaleQuestion

    answer_option_range = random.choice(['value', 'agreement'])


class QualitativeAnswerFactory(factory.DjangoModelFactory):
    """Factory for qualitative answers."""
    class Meta:
        model = models.QualitativeAnswer

    learner = factory.SubFactory(UserFactory)
    question = factory.SubFactory(QualitativeQuestionFactory)


class KnowledgeComponentFactory(factory.DjangoModelFactory):
    """Factory for knowledge components."""
    class Meta:
        model = models.KnowledgeComponent
        django_get_or_create = ['kc_id']


class SubmissionFactory(factory.DjangoModelFactory):
    """Factory for submissions."""
    class Meta:
        model = models.Submission
        django_get_or_create = ['section', 'learner']

    section = factory.SubFactory(SectionFactory)
    learner = factory.SubFactory(UserFactory)


class LPDExportFactory(factory.DjangoModelFactory):
    """Factory for LPD exports."""
    class Meta:
        model = models.LPDExport
        django_get_or_create = ['requested_by', 'requested_for']
