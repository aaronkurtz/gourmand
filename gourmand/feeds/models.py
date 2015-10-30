from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone

import dateutil.parser

from feeds.utils import tzd

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

class ArticleManager(models.Manager):
    def create_from_entry(self, entry):
        '''
        Create and return an Article object from a FeedParserDict's Entry
        '''
        # TODO Handle multiple links
        main_link = entry.get('link', '')
        title = entry.get('title', main_link)
        when_unparsed = entry.get('updated', entry.get('published', entry.get('created', None)))
        if when_unparsed:
            when = dateutil.parser.parse(when_unparsed, fuzzy=True, tzinfos=tzd)
            if timezone.is_naive(when):
                when = timezone.make_aware(when)
        else:
            when = timezone.now()
        gid = entry.get('id', main_link)
        # TODO Handle multiple contents
        summary = entry.get('summary', None)
        if summary:
            main_content = summary
        else:
            try:
                main_content = entry['content'][0].value
            except KeyError:
                main_content = title

        return Article(when=when, main_link=main_link, title=title, gid=gid, main_content=main_content)


class Article(models.Model):
    feed = models.ForeignKey(Feed)
    when = models.DateTimeField()
    title = models.TextField()
    gid = models.TextField(verbose_name="Global Identifier", validators=[MinLengthValidator(1, message="GID can not be blank")])
    main_content = models.TextField()
    main_link = models.URLField(max_length=URL_MAX_LEN)

    objects = ArticleManager()

    def __str__(self):
        return self.gid

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
