from django import template

register = template.Library()


@register.filter(name='range')
def option_range(count):
    return range(1, int(count) + 1)
