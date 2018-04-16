# Constants for Learner Profile Dashboard


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
    def get_qualitative_types(cls):
        """
        Return iterable of qualitative question types.
        """
        return cls.ESSAY, cls.SHORT_ANSWER
