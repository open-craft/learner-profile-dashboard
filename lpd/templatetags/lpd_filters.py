"""
Custom template filters for Learner Profile Dashboard
"""

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
    return mark_safe(markdown(string))
