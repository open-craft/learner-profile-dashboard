"""
Factories for Learner Profile Dashboard tests
"""

import random

from django.contrib.auth import get_user_model
import factory

from lpd.constants import QuestionTypes
from lpd.models import (
    KnowledgeComponent,
    LearnerProfileDashboard,
    LikertScaleQuestion,
    MultipleChoiceQuestion,
    QualitativeAnswer,
    QualitativeQuestion,
    RankingQuestion,
    Section
)


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
        model = LearnerProfileDashboard
        django_get_or_create = ['name']

    name = factory.Sequence(u'LPD {0}'.format)


class SectionFactory(factory.DjangoModelFactory):
    """Factory for sections."""
    class Meta:
        model = Section
        django_get_or_create = ['title']

    lpd = factory.SubFactory(LearnerProfileDashboardFactory)
    title = factory.Sequence(u'Section {0}'.format)


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
        model = QualitativeQuestion

    question_type = random.choice(QuestionTypes.get_qualitative_types())


class MultipleChoiceQuestionFactory(QuestionFactory):
    """Factory for multiple choice questions."""
    class Meta:
        model = MultipleChoiceQuestion

    max_options_to_select = random.randint(1, 15)


class RankingQuestionFactory(QuestionFactory):
    """Factory for ranking questions."""
    class Meta:
        model = RankingQuestion

    number_of_options_to_rank = random.randint(1, 5)


class LikertScaleQuestionFactory(QuestionFactory):
    """Factory for Likert scale questions."""
    class Meta:
        model = LikertScaleQuestion

    answer_option_range = random.randint(1, 10)


class QualitativeAnswerFactory(factory.DjangoModelFactory):
    """Factory for qualitative answers."""
    class Meta:
        model = QualitativeAnswer
        django_get_or_create = ['learner', 'question']

    learner = factory.SubFactory(UserFactory)
    question = factory.SubFactory(QualitativeQuestionFactory)


class KnowledgeComponentFactory(factory.DjangoModelFactory):
    """Factory for knowledge components."""
    class Meta:
        model = KnowledgeComponent
        django_get_or_create = ['kc_id']
