from collections import Counter
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.urlresolvers import reverse_lazy
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import pluralize
from django.views.generic import TemplateView, ListView, FormView, View, RedirectView, DetailView, DeleteView

from async_messages import messages as async_messages
from braces.views import LoginRequiredMixin, UserFormKwargsMixin
from django_q.tasks import async, async_iter, result
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
        urls = {f.get('xmlUrl', None) for f in feeds}
        existing_subscriptions = Subscription.objects.filter(owner=self.request.user, feed__href__in=urls)
        existing_urls = set(existing_subscriptions.values_list('feed__href', flat=True))
        fresh_urls = urls - existing_urls
        num_existing = len(existing_urls)
        num_fresh = len(fresh_urls)
        if fresh_urls:
            async(import_urls, self.request.user, fresh_urls)
        if num_fresh:
            messages.success(self.request, "You imported {sub} feed{s} - processing now.".format(sub=num_fresh, s=pluralize(num_fresh)))
        if num_existing:
            messages.info(self.request,
                          "You were already subscribed to {sub_exists} feed{s}.".format(sub_exists=num_existing, s=pluralize(num_existing)))
        return super(self.__class__, self).form_valid(form)


def import_urls(user, fresh_urls):
    result_id = async_iter(subscribe_to_imported_url, [(user, url) for url in fresh_urls], timeout=30)
    import_results = Counter(result(result_id, -1))
    print("Results", import_results)
    added = import_results['added']
    existed = import_results['existed']
    errors = import_results['errors']
    async_messages.success(user, "Import complete - you subscribed to {sub} feed{s}.".format(sub=added, s=pluralize(added)))
    if existed:
        async_messages.info(user,
                            "You were already subscribed to {sub_exists} imported feed{s}.".format(sub_exists=existed, s=pluralize(existed)))
    if errors:
        async_messages.error(user, "There was an error subscribing to {errors} imported feed{s}.".format(errors=errors, s=pluralize(errors)))


def subscribe_to_imported_url(user, url):
    try:
        try:
            feed = Feed.objects.get(href=url)
        except Feed.DoesNotExist:
            fp = feedparser.parse(url)
            feed = Feed.objects.create_from_feed(fp)
            feed.full_clean()
            feed.save()
            feed.update(fp)
        sub, created = Subscription.objects.get_or_create(owner=user, feed=feed)
        sub.populate()
        if created:
            return('added')
        else:
            return('existed')
    except ValidationError:
        return('error')


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
