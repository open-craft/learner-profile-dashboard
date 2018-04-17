# Constants for Learner Profile Dashboard


# Exceptions

class UnknownQuestionTypeError(ValueError):
    """
    Raised when encountering an unknown question type.
    """
    def __init__(self, question_type, *args, **kwargs):
        super(UnknownQuestionTypeError, self).__init__(
            'Unknown question type: {question_type}. '
            'Known types are: {question_types}.'.format(
                question_type=question_type,
                question_types=QuestionTypes.get_all()
            )
        )


# Classes

class QuestionTypes(object):
    """
    Lists valid question types.
    """
    ESSAY = 'essay'
    SHORT_ANSWER = 'short-answer'
    MCQ = 'mcq'
    MRQ = 'mrq'
    RANKING = 'ranking'
    LIKERT = 'likert'

    @classmethod
    def get_multiple_choice_types(cls):
        """
        Return iterable of multiple choice question types.
        """
        return cls.MCQ, cls.MRQ

    @classmethod
    def get_quantitative_types(cls):
        """
        Return iterable of quantitative question types.
        """
        return cls.get_multiple_choice_types() + (cls.RANKING, cls.LIKERT)

    @classmethod
    def get_qualitative_types(cls):
        """
        Return iterable of qualitative question types.
        """
        return cls.ESSAY, cls.SHORT_ANSWER

    @classmethod
    def get_all(cls):
        """
        Return iterable of all available question types.
        """
        return cls.get_qualitative_types() + cls.get_quantitative_types()
