import logging

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

import dateutil.parser
import feedparser
import requests

from feeds.utils import tzd, chain_gets

URL_MAX_LEN = 2048
FEED_GET_TIMEOUT = 10

USER_AGENT = feedparser.USER_AGENT

logger = logging.getLogger(__name__)


class FeedManager(models.Manager):
    def get_feed(self, url):
        '''
        Takes a URL and creates or retrieves the corresponding feed.
        '''
        if Feed.objects.filter(href=url).exists():
            return Feed.objects.get(href=url)
        try:
            r = requests.get(url, timeout=FEED_GET_TIMEOUT, headers={'User-Agent': USER_AGENT})
        except requests.exceptions.RequestException:
            raise ValidationError('Unable to retrieve %(url)s', code='connection_error', params={'url': url})
        new_url = r.url
        if url != new_url and Feed.objects.filter(href=new_url).exists():
            return Feed.objects.get(href=r.url)

        fp = feedparser.parse(r.content)
        fp['href'] = new_url
        feed = self.create_from_feed(parsed_feed=fp)
        feed.etag = r.headers.get('ETag', '')
        feed.last_modified = r.headers.get('Last-Modified', '')
        feed.full_clean()
        feed.save()
        feed.update(parsed_feed=fp)
        return feed

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
    etag = models.TextField(editable=False, blank=True, default='')
    last_modified = models.TextField(editable=False, blank=True, default='')

    objects = FeedManager()

    def __str__(self):
        return self.href

    def get_parsed(self):
        headers = {'User-Agent': USER_AGENT, 'If-None-Match': self.etag, 'If-Modified-Since': self.last_modified}
        r = requests.get(self.href, timeout=FEED_GET_TIMEOUT, headers=headers)
        if r.status_code == 304:
            return None
        self.etag = r.headers.get('ETag', '')
        self.last_modified = r.headers.get('Last-Modified', '')
        self.save()
        fp = feedparser.parse(r.content)
        fp['href'] = r.url
        return fp

    def update(self, parsed_feed=None):
        if not parsed_feed:
            parsed_feed = self.get_parsed()
            if not parsed_feed:
                return
        if parsed_feed.version == '':
            raise ValidationError('Version not found - unable to find proper RSS/Atom feed at %(href)s', code='invalid', params={'href': parsed_feed.href})
        # TODO handle updated feeds
        for entry in parsed_feed.entries:
            try:
                article = Article.objects.create_from_entry(entry)
            except Exception as e:
                logger.error('Unable to create article from feed {} - {}'.format(self.href, e))
                return
            if not Article.objects.filter(feed=self, gid=article.gid).exists():
                # TODO handle updated article
                article.feed = self
                article.save()


class ArticleManager(models.Manager):
    def create_from_entry(self, entry):
        '''
        Create and return an Article object from a FeedParserDict's Entry
        '''
        # TODO Handle multiple links
        main_link = entry.get('link', '')
        title = chain_gets(entry, ('title', 'link', 'id'))
        if not title:
            raise ValidationError("Title not found - unable to save Article", code='missing_title', params={})
        when_unparsed = chain_gets(entry, ['updated', 'published', 'created'])
        if when_unparsed:
            when = dateutil.parser.parse(when_unparsed, fuzzy=True, tzinfos=tzd)
            if timezone.is_naive(when):
                when = timezone.make_aware(when)
        else:
            when = timezone.now()
        gid = entry.get('id', main_link)
        if not gid:
            gid = slugify(title)
            if when_unparsed:
                gid = "{}@{}".format(when.timestamp(), gid)
        # TODO Handle multiple contents
        summary = entry.get('summary', None)
        if summary:
            main_content = summary
        else:
            try:
                main_content = entry['content'][0].value
            except KeyError:
                main_content = title

        if entry.get('link', None) is None and 'links' in entry:
            raise ValidationError("Link not found but links found - unable to save Article", code='missing_link', params={})
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
