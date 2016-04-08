from django import http, shortcuts


def dashboard(request):
    return HttpResponse(template=loader.get_template('/templates/dashboard.html'))


def search(request, **kwargs):
  context = {}
  return shortcuts.render(request, 'search.html', context)
