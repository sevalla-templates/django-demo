import os

import django
from django.http import HttpResponse
from django.template import engines


def django_default_view(request):
    """A view that returns the default Django bootstrap template."""
    path = os.path.join(os.path.dirname(django.__file__), 'views', 'templates', 'default_urlconf.html')
    template = engines['django'].from_string(open(path).read())
    return HttpResponse(template.render({}, request))
