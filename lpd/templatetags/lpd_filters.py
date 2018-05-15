"""
Custom template filters for Learner Profile Dashboard
"""

from django import template

register = template.Library()


@register.filter(name='range')
def option_range(count):
    """
    Return range from 1 to `count`, including `count`.
    """
    return range(1, int(count) + 1)
