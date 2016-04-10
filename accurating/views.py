from django import http, shortcuts, forms


def dashboard(request, **kwargs):
  class ASINForm(forms.Form):
    ASIN = forms.CharField(max_length=100)

  context = {'form': ASINForm()}
  return shortcuts.render(request, 'dashboard.html', context)


def search(request, **kwargs):
  context = {}
  return shortcuts.render(request, 'search.html', context)
