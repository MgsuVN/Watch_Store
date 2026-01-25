from django import template

register = template.Library()

@register.filter
def vnd(value):
    try:
        value = int(value)
        return "{:,}".format(value).replace(",", ".")
    except:
        return value
