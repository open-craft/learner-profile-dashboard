from django import forms
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from ordered_model.models import OrderedModel


class LearnerProfileDashboard(models.Model):
    name = models.TextField(help_text='Name of this LPD instance')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def get_absolute_url(self):
        return reverse('lpd:view', kwargs=dict(pk=self.id))


class LearnerProfileDashboardForm(forms.ModelForm):
    class Meta:
        model = LearnerProfileDashboard
        fields = ['name']


class Section(OrderedModel):
    """
    Groups a set of related questions on the LPD.
    """
    lpd = models.ForeignKey(
        'LearnerProfileDashboard',
        related_name='sections',
    )
    title = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text='Text to display above questions belonging to this section (optional).',
    )

    order_with_respect_to = 'lpd'

    class Meta(OrderedModel.Meta):
        pass

    def __unicode__(self):
        return 'Section {id}: {title}'.format(id=self.id, title=self.title or '<title not set>')

    @property
    def questions(self):
        """
        Return list of all questions belonging to this section, irrespective of their type.
        """
        return sorted(
            list(self.qualitativequestion_set.all()) +
            list(self.multiplechoicequestion_set.all()) +
            list(self.rankingquestion_set.all()) +
            list(self.likertscalequestion_set.all()),
            key=lambda q: q.section_number
        )


class Question(models.Model):
    """
    Abstract base class for models representing learner profile question.
    """
    section = models.ForeignKey('Section')
    number = models.PositiveIntegerField(
        default=1,
        help_text='Number of this question relative to parent section.'
    )
    question_text = models.TextField(
        help_text='Text to display above answer options (if any) and input fields.',
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Author notes about this question (optional).',
    )

    class Meta:
        abstract = True

    @property
    def type(self):
        """
        Return string that specifies the exact type of this question.
        """
        raise NotImplementedError

    @property
    def section_number(self):
        """
        Return string of the form 'X.Y'
        where X represents `order` of parent section and Y represents `number` of this question.
        """
        return '{section}.{number}'.format(section=self.section.order, number=self.number)


class QualitativeQuestion(Question):
    """
    Represents a questions that requires a free-text answer.
    """
    SHORT_ANSWER = 'short answer'
    ESSAY = 'essay'
    QUESTION_TYPES = (
        ('short-answer', SHORT_ANSWER),
        ('essay', ESSAY),
    )
    question_type = models.CharField(
        choices=QUESTION_TYPES,
        max_length=20,
        help_text='Whether this question requires learners to produce a short answer or an essay.',
    )
    influences_group_membership = models.BooleanField(
        default=False,
        help_text=(
            'Whether answers to this question should be taken into account '
            'when calculating group membership for specific learners.'
        ),
    )

    def __unicode__(self):
        return 'QualitativeQuestion {id}: {text}'.format(id=self.id, text=self.question_text)

    @property
    def type(self):
        """
        Return string that specifies the exact type of this question.
        """
        return self.question_type


class QuantitativeQuestion(Question):
    """
    Abstract base class for models representing questions with a pre-defined set of answer options.
    """
    answer_options = GenericRelation('AnswerOption')
    randomize_options = models.BooleanField(
        default=False,
        help_text='Whether to display answer options in random order on LPD.',
    )

    class Meta:
        abstract = True

    def get_content_type(self):
        return ContentType.objects.get_for_model(self).id

    @property
    def type(self):
        """
        Return string that specifies the exact type of this question.
        """
        raise NotImplementedError

    def get_answer_options(self):
        """
        Return answer options belonging to this question, sorted according to value of `randomize_options`:

        - If `randomize_options` is True, return answer options in random order.
        - If `randomize_options` is False, return answer options in alphabetical order (based on `option_text`).
        """
        ordering = '?' if self.randomize_options else 'option_text'
        return self.answer_options.order_by(ordering)


class MultipleChoiceQuestion(QuantitativeQuestion):
    """
    Represents a multiple choice question (MCQ) or multiple response question (MRQ).
    """
    max_options_to_select = models.PositiveIntegerField(
        default=1,
        help_text=(
            'Maximum number of answer options that learner is allowed to select for this question. '
            'Set this to 1 to create a multiple choice question. '
            'Set this to a value larger than one to create a multiple response question.'
        ),
    )

    def __unicode__(self):
        return 'MultipleChoiceQuestion {id}: {text}'.format(id=self.id, text=self.question_text)

    @property
    def type(self):
        """
        Return string that specifies the exact type of this question.
        """
        return 'mcq' if self.max_options_to_select == 1 else 'mrq'


class RankingQuestion(QuantitativeQuestion):
    """
    Represents a question that asks learners to rank (a subset of) its answer options,
    on a scale from 1 to `number_of_options_to_rank`.
    """
    number_of_options_to_rank = models.PositiveIntegerField(
        default=3,
        help_text='Number of answer options belonging to this question that learners are allowed to rank.',
    )

    def __unicode__(self):
        return 'RankingQuestion {id}: {text}'.format(id=self.id, text=self.question_text)

    @property
    def type(self):
        """
        Return string that specifies the exact type of this question.
        """
        return 'ranking'


class LikertScaleQuestion(QuantitativeQuestion):
    """
    Represents a (simplified) Likert Scale question, cf. https://en.wikipedia.org/wiki/Likert_scale.
    """
    answer_option_range = models.PositiveIntegerField(
        default=5,
        help_text=(
            'Number of values that learners can choose from for each answer option. '
            'For example, to create 5-point scale, set this to 5.'
        ),
    )
    range_min_text = models.CharField(
        max_length=50,
        default='strongly disagree',
        help_text='Meaning of lowest value of Likert scale. For example: "Not very valuable".',
    )
    range_max_text = models.CharField(
        max_length=50,
        default='strongly agree',
        help_text='Meaning of highest value of Likert scale. For example: "Extremely valuable."',
    )

    def __unicode__(self):
        return 'LikertScaleQuestion {id}: {text}'.format(id=self.id, text=self.question_text)

    @property
    def type(self):
        """
        Return string that specifies the exact type of this question.
        """
        return 'likert'


class AnswerOption(models.Model):
    """
    Represents a specific answer option for a quantitative learner profile question.
    """
    # Use generic relation to connect this model to QuantitativeQuestion (which is abstract).
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    knowledge_component = models.OneToOneField(
        'KnowledgeComponent',
        blank=True,
        null=True,
        help_text='Knowledge component that this answer option is associated with.',
    )
    option_text = models.TextField(
        help_text='Text to display for this answer option.',
    )
    allows_custom_input = models.BooleanField(
        default=False,
        help_text=(
            'Whether this option allows learners to specify custom input. '
            'For example, a quantitative question might include an "Other" option '
            'that allows learners to specify what that option represents. '
            'The LPD will render this as: '
            'Other: ______________.'
        ),
    )
    influences_recommendations = models.BooleanField(
        default=False,
        help_text=(
            'Whether answers to this answer option '
            'should be sent to the adaptive engine to tune recommendations.'
        ),
    )

    class Meta:
        ordering = ["-option_text"]

    def __unicode__(self):
        return 'AnswerOption {id}: {text}'.format(id=self.id, text=self.option_text)


class Answer(models.Model):
    """
    Abstract base class for models representing learner answers to LPD questions.
    """
    learner = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        abstract = True


class QualitativeAnswer(Answer):
    """
    Represents a learner's answer to a qualitative question.
    """
    question = models.ForeignKey(
        'QualitativeQuestion',
        related_name='learner_answers',
    )
    text = models.TextField(
        help_text='Answer that the learner provided to the associated question.',
    )

    def __unicode__(self):
        return 'QualitativeAnswer {id}: {text}'.format(id=self.id, text=self.text)


class QuantitativeAnswer(Answer):
    """
    Represents a learner's answer to a specific answer option of a quantitative question.
    """
    answer_option = models.ForeignKey(
        'AnswerOption',
        related_name='learner_answers',
    )
    value = models.PositiveIntegerField(
        help_text='The value that the learner chose for the associated question.',
    )
    custom_input = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text='The input that a learner provided for a quantitative question that `allows_custom_input`.',
    )

    def __unicode__(self):
        return 'QuantitativeAnswer {id}: {value}'.format(id=self.id, value=self.value)


class KnowledgeComponent(models.Model):
    """
    Represents a knowledge component (tag) that the adaptive engine uses to track topic mastery.

    A knowledge component is either associated with a specific answer option,
    or represents a 'group' that a learner might be associated with.
    """
    kc_id = models.CharField(
        max_length=50,
        help_text='String that LPD and adaptive engine use to uniquely identify this knowledge component.',
    )
    kc_name = models.CharField(
        max_length=100,
        help_text='Verbose name for this knowledge component.',
    )

    def __unicode__(self):
        return 'KnowledgeComponent {id}: {kc_id}, {kc_name}'.format(id=self.id, kc_id=self.kc_id, kc_name=self.kc_name)


class Score(models.Model):
    """
    Represents a learner's score for a specific knowledge node.

    For a knowledge component that represents a group,
    the score is equal to the probability of the learner belonging to that group.

    For a knowledge component that is associated with an answer option,
    the score represents the transformed value of the learner's answer to that answer option.
    """
    knowledge_component = models.OneToOneField('KnowledgeComponent')
    learner = models.OneToOneField(settings.AUTH_USER_MODEL)
    value = models.FloatField(
        help_text="The learner's score for the associated knowledge component.",
    )

    def __unicode__(self):
        return 'Score {id}: {value}'.format(id=self.id, value=self.value)
