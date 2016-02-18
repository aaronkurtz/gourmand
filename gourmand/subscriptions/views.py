from django.contrib import messages
from django.contrib.auth import get_user
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.db.models import Count, Max, Case, When
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import pluralize
from django.views.generic import TemplateView, ListView, FormView, View, RedirectView, DetailView, DeleteView, UpdateView

from braces.views import LoginRequiredMixin, UserFormKwargsMixin
from django_q.tasks import async

from .async import import_urls
from .forms import NewSubForm, ImportOPMLForm, UpdateSubscriptionForm
from .models import Subscription, PersonalArticle, Category
from .utils import create_opml


class Account(LoginRequiredMixin, TemplateView):
    template_name = "account/index.html"


class DeleteAccount(LoginRequiredMixin, DeleteView):
    template_name = "account/delete.html"
    success_url = reverse_lazy('front')

    def get_object(self, queryset=None):
        return get_user(self.request)


class Reader(LoginRequiredMixin, TemplateView):
    template_name = "reader.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subs = Subscription.objects.filter(owner=self.request.user).select_related('feed').order_by('title')

        active_cat = None
        if self.request.GET.get('reset', None):
            self.request.session.pop('active_cat', None)
        else:
            active_cat = self.request.GET.get('category', self.request.session.get('active_cat', None))
            if active_cat:
                try:
                    category = Category.objects.get(owner=self.request.user, name=active_cat)
                    context['active_cat_name'] = category.name
                    self.request.session['active_cat'] = category.name
                    active_cat = category.id
                    subs = subs.filter(category=category)
                except Category.DoesNotExist:
                    active_cat = None

        context['active_cat'] = active_cat
        categories = Category.objects.get_user_categories(self.request.user).order_by('-order')
        context['categories'] = categories

        reading = self.request.GET.get('reading', self.request.session.get('reading', 'unread'))
        if reading not in ('unread', 'saved', 'all'):
            reading = 'unread'
        self.request.session['reading'] = reading
        if reading == 'unread':
            # FIXME N+1 query
            for cat in categories:
                cat.count = Subscription.objects.filter(category=cat).aggregate(count=Count(Case(When(personalarticle__active=True, then=1))))['count']
            # Extra modifier is required to annotate unread as well as articles
            # Conditional Count in 1.8 works, but breaks if combined with another Count, despite using distinct=True
            subs = subs.extra(
                select={'count': 'SELECT COUNT(*) FROM subscriptions_personalarticle WHERE ' +
                        'subscriptions_subscription.id = subscriptions_personalarticle.sub_id AND active IS TRUE'})
            subs = filter(lambda x: x.count, subs)
            context['count_all'] = PersonalArticle.objects.filter(sub__owner=self.request.user, active=True).count()
        elif reading == 'saved':
            for cat in categories:
                cat.count = Subscription.objects.filter(category=cat).aggregate(count=Count(Case(When(personalarticle__archived=True, then=1))))['count']
            subs = subs.extra(
                select={'count': 'SELECT COUNT(*) FROM subscriptions_personalarticle WHERE ' +
                        'subscriptions_subscription.id = subscriptions_personalarticle.sub_id AND archived IS TRUE'})
            subs = filter(lambda x: x.count, subs)
            context['count_all'] = PersonalArticle.objects.filter(sub__owner=self.request.user, archived=True).count()
        else:
            context['count_all'] = PersonalArticle.objects.count()
            for cat in categories:
                cat.count = Subscription.objects.filter(category=cat).aggregate(count=Count('personalarticle'))['count']
            subs = subs.annotate(count=Count('personalarticle'))

        context['subs'] = subs
        context['reading'] = reading
        return context


class PostsList(LoginRequiredMixin, ListView):
    model = PersonalArticle
    context_object_name = 'posts'
    template_name = "subscriptions/posts.html"

    def get_queryset(self):
        self.sub = get_object_or_404(Subscription, pk=self.kwargs['pk'])
        if self.sub.owner != self.request.user:
            raise PermissionDenied

        posts = PersonalArticle.objects.filter(sub=self.sub).select_related('article').order_by('article__when')

        reading = self.request.GET.get('reading', self.request.session.get('reading', 'unread'))
        if reading not in ('unread', 'saved', 'all'):
            reading = 'unread'
        self.request.session['reading'] = reading
        self.reading = reading

        if reading == 'unread':
            posts = posts.filter(active=True)
        elif reading == 'saved':
            posts = posts.filter(archived=True)
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub'] = self.sub
        context['reading'] = self.reading
        return context


class AddSubscription(LoginRequiredMixin, UserFormKwargsMixin, FormView):
    form_class = NewSubForm
    template_name = "subscriptions/add_subscription.html"
    success_url = reverse_lazy('reader')

    def form_valid(self, form):
        feed = form.cleaned_data['feed']
        existing_category = form.cleaned_data['existing_category']
        new_category = form.cleaned_data['new_category']
        if existing_category:
            category = existing_category
        elif new_category:
            max_order = Category.objects.filter(owner=self.request.user).aggregate(Max('order'))['order__max']
            category = Category.objects.create(owner=self.request.user, name=new_category, order=max_order+1)
        else:
            category = Category.objects.get(owner=self.request.user, name='Uncategorized')
        sub = Subscription.objects.create(owner=self.request.user, feed=feed, category=category, title=feed.title)
        sub.populate()
        messages.success(self.request, "You have subscribed to <strong>{feed}</strong>".format(feed=sub.title))
        return super().form_valid(form)


class UpdateSubscription(LoginRequiredMixin, UserFormKwargsMixin, UpdateView):
    form_class = UpdateSubscriptionForm
    context_object_name = 'subscription'
    template_name = 'subscriptions/update_subscription.html'

    def get_queryset(self):
        return Subscription.objects.filter(owner=self.request.user).select_related('feed', 'category')

    def form_valid(self, form):
        new_category = form.cleaned_data['new_category']
        if new_category:
            max_order = Category.objects.filter(owner=self.request.user).aggregate(Max('order'))['order__max']
            category = Category.objects.create(owner=self.request.user, name=new_category, order=max_order+1)
            form.instance.category = category

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('subscription', args=[self.object.pk])


class MarkRead(LoginRequiredMixin, UpdateView):
    template_name = 'subscriptions/mark_read.html'
    context_object_name = 'subscription'
    fields = ()

    def get_queryset(self):
        return Subscription.objects.filter(owner=self.request.user)

    def get_success_url(self):
        count = self.object.personalarticle_set.filter(active=True).update(active=False)
        messages.success(self.request,
                         "You marked {count} article{s} in {title} as read".format(
                             count=count, s=pluralize(count), title=self.object.title))
        return reverse_lazy('reader')


class RemoveSubscription(LoginRequiredMixin, DeleteView):
    context_object_name = 'subscription'

    def get_queryset(self):
        return Subscription.objects.filter(owner=self.request.user).select_related('feed')

    def get_success_url(self):
        messages.success(self.request, "You unsubscribed from {title}".format(title=self.object.title))
        return reverse_lazy('reader')


class ImportOPML(LoginRequiredMixin, UserFormKwargsMixin, FormView):
    form_class = ImportOPMLForm
    template_name = "subscriptions/import_opml.html"
    success_url = reverse_lazy('reader')

    def form_valid(self, form):
        feeds = form.cleaned_data['feeds']
        mark_read = form.cleaned_data['mark_read']
        urls = {f.get('xmlUrl', None) for f in feeds}
        existing_subscriptions = Subscription.objects.filter(owner=self.request.user, feed__href__in=urls)
        existing_urls = set(existing_subscriptions.values_list('feed__href', flat=True))
        fresh_urls = urls - existing_urls
        num_existing = len(existing_urls)
        num_fresh = len(fresh_urls)
        if fresh_urls:
            async(import_urls, self.request.user, fresh_urls, mark_read, group='opml_import')
        if num_fresh:
            messages.success(self.request, "You imported {sub} feed{s} - processing now.".format(sub=num_fresh, s=pluralize(num_fresh)))
        if num_existing:
            messages.info(self.request,
                          "You were already subscribed to {sub_exists} feed{s}.".format(sub_exists=num_existing, s=pluralize(num_existing)))
        return super().form_valid(form)


class ExportOPML(LoginRequiredMixin, View):
    def get(self, request):
        opml = create_opml(request.user)
        response = HttpResponse(opml, content_type='text/x-opml')
        response['Content-Disposition'] = 'attachment; filename="gourmand.opml"'
        return response


class ReadOldest(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        sub = get_object_or_404(Subscription, owner=self.request.user, pk=kwargs['pk'])
        reading = self.request.session.get('reading', 'unread')
        filter_args = {'sub': sub}
        if reading == 'unread':
            filter_args['active'] = True
        elif reading == 'saved':
            filter_args['archived'] = True
        try:
            oldest = PersonalArticle.objects.select_related('article').filter(**filter_args).earliest('article__when')
            return reverse_lazy('article', args=[oldest.pk])
        except PersonalArticle.DoesNotExist:
            return reverse_lazy('reader')


class ArticleNav(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        try:
            post = PersonalArticle.objects.select_related('article').get(pk=kwargs['pk'], sub__owner=self.request.user)
            reading = self.request.session.get('reading', 'unread')
            filter_args = {'sub': post.sub}
            if reading == 'unread':
                filter_args['active'] = True
            elif reading == 'saved':
                filter_args['archived'] = True
            qs = PersonalArticle.objects.select_related('article').filter(**filter_args)
            if kwargs['dir'] == 'old':
                nav_to = qs.filter(article__when__lt=post.article.when).latest('article__when')
            else:
                nav_to = qs.filter(article__when__gt=post.article.when).earliest('article__when')
            return reverse_lazy('article', args=[nav_to.pk])
        except PersonalArticle.DoesNotExist:
            return reverse_lazy('reader')


class ArticleToggleSave(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        try:
            post = PersonalArticle.objects.get(pk=kwargs['pk'], sub__owner=self.request.user)
            post.archived = not post.archived
            post.save()
            return reverse_lazy('article', args=[post.pk])
        except PersonalArticle.DoesNotExist:
            return reverse_lazy('reader')


class ArticleReader(LoginRequiredMixin, DetailView):
    context_object_name = "post"

    def get_queryset(self):
        return PersonalArticle.objects.filter(sub__owner=self.request.user).select_related('article', 'sub', 'sub__feed')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.active = False
        obj.save()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reading = self.request.GET.get('reading', self.request.session.get('reading', 'unread'))
        if reading not in ('unread', 'saved', 'all'):
            reading = 'unread'
        self.request.session['reading'] = reading
        context['reading'] = reading
        return context
