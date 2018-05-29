"""
Custom template filters for Learner Profile Dashboard
"""

import re

from django import template
from django.utils.safestring import mark_safe
from markdown import markdown

register = template.Library()


@register.filter(name='range')
def option_range(count):
    """
    Return range from 1 to `count`, including `count`.
    """
    return range(1, int(count) + 1)


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
