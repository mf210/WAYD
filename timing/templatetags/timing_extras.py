from django import template


register = template.Library()

@register.filter
def hours_and_minutes(value):
    return f'{value // 60}h {value % 60:0>2}m'
