from django import template

register = template.Library()

@register.simple_tag
def replace(request, field, value):

    dict_ = request.GET.copy()

    dict_[field] = value

    return dict_.urlencode()

# Use as:

# <a href="?{% replace request 'param' value %}">

