from django.core.exceptions import ValidationError
from django.db import models

URL_MAX_LEN = 2048


class FeedManager(models.Manager):
    def create_from_feed(self, parsed_feed, href=None):
        '''
        Create and return a Feed object from a FeedParserDict
        '''
        href = parsed_feed.get('href', href)  # Use Feedparser's HREF if available, otherwise use argument
        if not href:
            raise ValidationError('HREF not found - unable to create feed', code='missing_href', params={})
        if parsed_feed.version == '':
            raise ValidationError('Version not found - unable to find proper RSS/Atom feed at %(href)s', code='invalid', params={'href': href})
        title = parsed_feed.feed.get('title', href)
        link = parsed_feed.feed.get('link', '')
        feed = Feed(title=title, href=href, link=link)
        return feed


class Feed(models.Model):
    href = models.URLField(max_length=URL_MAX_LEN, unique=True, verbose_name="HREF")
    link = models.URLField(max_length=URL_MAX_LEN, blank=True)
    title = models.TextField()

    objects = FeedManager()

    def __str__(self):
        return self.href


class Article(models.Model):
    feed = models.ForeignKey(Feed)
    when = models.DateTimeField()
    title = models.TextField()
    gid = models.TextField(verbose_name="Global Identifier")
    main_content = models.TextField()
    main_link = models.URLField(max_length=URL_MAX_LEN)

    class Meta:
        unique_together = ('feed', 'gid')


class ExtraContent(models.Model):
    article = models.ForeignKey(Article)
    content = models.TextField()


class ExtraLink(models.Model):
    article = models.ForeignKey(Article)
    rel = models.TextField()
    type = models.TextField()
    link = models.URLField(max_length=URL_MAX_LEN)
