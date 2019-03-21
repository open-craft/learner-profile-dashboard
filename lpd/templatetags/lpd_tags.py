"""
Custom template tags for Learner Profile Dashboard
"""

import calendar

from django import template

from lpd.models import Submission

register = template.Library()


@register.simple_tag
def get_last_update(section, learner):
    """
    Return timestamp corresponding to date and time at which `learner` last submitted `section`.
    """
    last_update = Submission.get_last_update(section, learner)
    if last_update is not None:
        return calendar.timegm(last_update.timetuple())
    return last_update


@register.simple_tag
def get_answer(question, learner):
    """
    Return answer that `learner` provided for `question`.
    """
    return question.get_answer(learner)


@register.simple_tag
def get_data(answer_option, learner):
    """
    Return value that `learner` chose for `answer_option`.

    If `answer_option` belongs to a multiple choice question,
    the value returned will be 1 if the learner selected the answer option,
    and 0 if the learner did not select the answer option.
    """
    return answer_option.get_data(learner)
