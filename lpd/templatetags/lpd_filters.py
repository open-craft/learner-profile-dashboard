"""
Custom template filters for Learner Profile Dashboard
"""

import re

from django import template
from django.utils.safestring import mark_safe
from markdown import markdown

from lpd.models import LikertScaleQuestion

register = template.Library()


@register.filter()
def ranking_range(count):
    """
    Return range from 1 to `count`, including `count`.
    """
    return range(1, int(count) + 1)


@register.filter()
def likert_range(answer_option_range):
    """
    Return range from 1 to `count`, including `count`.
    """
    return enumerate(LikertScaleQuestion.ANSWER_OPTION_RANGES[answer_option_range], start=1)


@register.filter()
def render_custom_formatting(string):
    """
    Render custom formatting for `string`.

    Supports both Markdown and HTML formatting directives.
    """
    # Note that markdown callable wraps results in <p> tags, which is not what we want
    # (it breaks the LPD's layout and makes it harder to target elements from CSS).
    # So we remove these tags before returning the formatted string:
    formatted_string = re.sub('</?p>', '', markdown(string))
    return mark_safe(formatted_string)


@register.filter()
def remove_estimates(string):
    """
    Remove paragraph(s) providing effort estimates from `string`.
    """
    return re.sub(
        r'This section should take approximately \d+ minutes'
        '(, though you are welcome to take as much time as you like)?.'
        '(<br />){0,2}',
        '',
        string
    )


@register.filter()
def remove_notes(string):
    """
    Remove notes from `string`.

    A note is any portion of the string that is wrapped in parentheses
    and follows the main, non-parenthesized portion of the string.
    """
    return re.sub(r' \(.+\)$', '', string)
