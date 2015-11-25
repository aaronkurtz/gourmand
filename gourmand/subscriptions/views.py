from django.db.models import Count
from django.views.generic import TemplateView, ListView

from braces.views import LoginRequiredMixin

from .models import Subscription


class FrontPage(TemplateView):
    template_name = "index.html"


class Reader(LoginRequiredMixin, ListView):
    template_name = "reader.html"

    def get_queryset(self):
        subs = Subscription.objects.filter(owner=self.request.user).select_related('feed')
        # Extra modifier is required to annotate unread as well as articles
        # Conditional Count in 1.8 works, but breaks if combined with another Count, despite using distinct=True
        subs = subs.annotate(articles=Count('feed__article')).\
            extra(select={'unread': 'SELECT COUNT(*) FROM subscriptions_personalarticle WHERE ' +
                          'subscriptions_subscription.id = subscriptions_personalarticle.sub_id AND active IS TRUE'})
        return subs
