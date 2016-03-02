from django import template

register = template.Library()

@register.simple_tag
def replace(request, field, value):

    try:
        dict_ = request.GET.copy()

        dict_[field] = value

        return dict_.urlencode()
    except Exception:
        return request

# Use as:

# <a href="?{% replace request 'param' value %}">

