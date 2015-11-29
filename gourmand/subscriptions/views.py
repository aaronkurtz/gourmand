from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, FormView

from braces.views import LoginRequiredMixin, UserFormKwargsMixin

from .forms import NewSubForm
from .models import Subscription, PersonalArticle


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


class PersonalArticleList(LoginRequiredMixin, ListView):
    model = PersonalArticle

    def get_queryset(self):
        self.sub = get_object_or_404(Subscription, pk=self.kwargs['pk'])
        if self.sub.owner != self.request.user:
            raise PermissionDenied
        return PersonalArticle.objects.filter(sub=self.sub).select_related('article').order_by('article__when')

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['sub'] = self.sub
        return context


class AddSubscription(LoginRequiredMixin, UserFormKwargsMixin, FormView):
    form_class = NewSubForm
    template_name = "subscriptions/add_subscription.html"
    success_url = reverse_lazy('reader')

    def form_valid(self, form):
        feed = form.cleaned_data['feed']
        sub = Subscription.objects.create(owner=self.request.user, feed=feed)
        sub.populate()
        messages.success(self.request, "You have subscribed to <strong>{feed}</strong>".format(feed=feed.title))
        return super(self.__class__, self).form_valid(form)
