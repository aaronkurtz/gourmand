from django.views.generic import TemplateView, ListView

from braces.views import LoginRequiredMixin

from .models import Subscription


class FrontPage(TemplateView):
    template_name = "index.html"


class Reader(LoginRequiredMixin, ListView):
    template_name = "reader.html"

    def get_queryset(self):
        return Subscription.objects.filter(owner=self.request.user).select_related('feed')
