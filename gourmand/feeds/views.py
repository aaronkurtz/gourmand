from django.db.models import Count
from django.views.generic import ListView
from django.shortcuts import get_object_or_404

from .models import Feed, Article


class FeedList(ListView):
    model = Feed
    queryset = Feed.objects.all().annotate(num_articles=Count('article'))


class ArticleList(ListView):
    model = Article

    def get_queryset(self):
        self.feed = get_object_or_404(Feed, pk=self.kwargs['pk'])
        return Article.objects.filter(feed=self.feed).order_by('when')

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['feed'] = self.feed
        return context
