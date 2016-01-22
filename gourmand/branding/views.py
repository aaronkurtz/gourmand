from django.views.generic import TemplateView
from django.shortcuts import redirect


class FrontPage(TemplateView):
    template_name = "index.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('reader')
        return super().dispatch(request, *args, **kwargs)
