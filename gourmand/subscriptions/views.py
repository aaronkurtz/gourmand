from collections import Counter

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.urlresolvers import reverse_lazy
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import pluralize
from django.views.generic import TemplateView, ListView, FormView, View, RedirectView, DetailView, DeleteView

from braces.views import LoginRequiredMixin, UserFormKwargsMixin
import feedparser

from feeds.models import Feed
from .forms import NewSubForm, ImportOPMLForm
from .models import Subscription, PersonalArticle
from .utils import create_opml


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
        subs = subs.order_by('feed__title')
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


class RemoveSubscription(LoginRequiredMixin, DeleteView):
    def get_queryset(self):
        return Subscription.objects.filter(owner=self.request.user).select_related('feed')

    def get_object(self, queryset=None):
        obj = super(self.__class__, self).get_object(queryset)
        self.title = obj.feed.title
        return obj

    def get_success_url(self):
        messages.success(self.request, "You unsubscribed from {title}".format(title=self.title))
        return reverse_lazy('reader')


class ImportOPML(LoginRequiredMixin, UserFormKwargsMixin, FormView):
    form_class = ImportOPMLForm
    template_name = "subscriptions/import_opml.html"
    success_url = reverse_lazy('reader')

    def form_valid(self, form):
        feeds = form.cleaned_data['feeds']
        # TODO Do this in an async task
        urls = [f.get('xmlUrl', None) for f in feeds]
        c = Counter()
        for url in urls:
            if Subscription.objects.filter(owner=self.request.user, feed__href=url).exists():
                c['sub_exists'] += 1
                continue
            if not Feed.objects.filter(href=url).exists():
                try:
                    fp = feedparser.parse(url)
                    feed = Feed.objects.create_from_feed(fp)
                    feed.save()
                    feed.update(fp)
                except ValidationError:
                    c['error'] += 1
                    continue
            else:
                feed = Feed.objects.get(href=url)
            sub = Subscription.objects.create(owner=self.request.user, feed=feed)
            sub.populate()
            c['subbed'] += 1
        if c['subbed']:
            messages.success(self.request, "You subscribed to {sub} feed{s}.".format(sub=c['subbed'], s=pluralize(c['subbed'])))
        if c['error']:
            messages.error(self.request, "There were errors importing {error} feed{s}.".format(error=c['error'], s=pluralize(c['error'])))
        if c['sub_exists']:
            messages.info(self.request,
                    "You were already subscribed to {sub_exists} feed{s}.".format(sub_exists=c['sub_exists'], s=pluralize(c['sub_exists'])))
        return super(self.__class__, self).form_valid(form)


class ExportOPML(LoginRequiredMixin, View):
    def get(self, request):
        opml = create_opml(request.user)
        response = HttpResponse(opml, content_type='text/x-opml')
        response['Content-Disposition'] = 'attachment; filename="gourmand.opml"'
        return response


class ReadNew(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        sub = get_object_or_404(Subscription, owner=self.request.user, pk=kwargs['pk'])
        try:
            oldest_unread = sub.personalarticle_set.filter(active=True).earliest('article__when')
            return reverse_lazy('article', args=[oldest_unread.pk])
        except PersonalArticle.DoesNotExist:
            return reverse_lazy('reader')


class ArticleReader(LoginRequiredMixin, DetailView):
    context_object_name = "personal_article"

    def get_queryset(self):
        return PersonalArticle.objects.filter(sub__owner=self.request.user).select_related('article', 'sub', 'sub__feed')

    def get_object(self, queryset=None):
        obj = super(self.__class__, self).get_object(queryset)
        obj.active = False
        obj.save()
        return obj
