from datetime import datetime

# from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

import feedparser

from feeds.models import Article


class ArticleTest(TestCase):
    def test_can_create_article(self):
        valid_feed = feedparser.parse('feeds/tests/testcases/atom_feed.xml')
        entry = valid_feed.entries[0]
        article, __, __ = Article.objects.create_from_entry(entry)
        self.assertEqual(article.title, 'Page 3')
        self.assertEqual(article.gid, 'https://www.comic-rocket.com/read/ow-my-sanity/3')
        self.assertEqual(article.main_content, '<a href="/read/ow-my-sanity/3">Ow My Sanity - Page 3</a>')
        self.assertEqual(article.main_link, 'https://www.comic-rocket.com/read/ow-my-sanity/3')
        self.assertEqual(str(article), article.gid)

    def test_tz_missing(self):
        feed = feedparser.parse('feeds/tests/testcases/tz_missing.rss')
        entry = feed.entries[0]
        article, __, __ = Article.objects.create_from_entry(entry)
        test_when = timezone.make_aware(datetime(2015, 9, 15, 0, 0))
        self.assertEqual(article.when, test_when)
