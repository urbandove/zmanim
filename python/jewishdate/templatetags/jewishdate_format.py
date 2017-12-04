from django import template
from .. import JewishDate, JewishCalendar


register = template.Library()

@register.filter
def jdate(value, format_string):
    if isinstance(value, JewishDate) or isinstance(value, JewishCalendar):
        return value.format(format_string)
    return ''