from django import http, shortcuts


def dashboard(request, **kwargs):
  context = {}
  return shortcuts.render(request, 'dashboard.html', context)


def search(request, **kwargs):
  context = {}
  return shortcuts.render(request, 'search.html', context)
