import markdown

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def codebook_markdown(value):
    return mark_safe(markdown.markdown(value)) # nosec

@register.simple_tag
def codebook_observed_value(value, variable):
    descriptions = variable.get('pdk_codebook_observed_descriptions', None)

    if descriptions is None:
        return value

    description = descriptions.get(value, None)

    if description is None:
        description = '*No description provided for **%s**.*' % value

    return mark_safe(markdown.markdown('%s: %s' % (value, description))) # nosec
