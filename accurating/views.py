from django.http import HttpResponse
from django.template import loader


def dashboard(request):
    return HttpResponse(template=loader.get_template('/templates/dashboard.html'))
