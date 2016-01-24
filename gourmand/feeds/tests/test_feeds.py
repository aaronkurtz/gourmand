from django.core.exceptions import ValidationError
from django.test import TestCase

import feedparser
from httmock import all_requests, HTTMock

from feeds.models import Feed


class FeedTests(TestCase):
    def test_can_create_from_good(self):
        valid_feed = feedparser.parse('feeds/tests/testcases/atom_feed.xml')
        feed = Feed.objects.create_from_feed(valid_feed, href="https://www.comic-rocket.com/explore/ow-my-sanity/rss")
        self.assertEqual(feed.title, "Ow My Sanity")
        self.assertEqual(feed.link, "https://www.comic-rocket.com/explore/ow-my-sanity/")
        self.assertEqual(feed.href, "https://www.comic-rocket.com/explore/ow-my-sanity/rss")
        self.assertEqual(str(feed), feed.href)

    def test_needs_href(self):
        hrefless_feed = feedparser.parse('feeds/tests/testcases/atom_feed.xml')
        with self.assertRaises(ValidationError) as cm:
            Feed.objects.create_from_feed(hrefless_feed)
        self.assertEqual(cm.exception.code, 'missing_href')

    def test_can_create_from_bad(self):
        bad_feed = feedparser.parse('feeds/tests/testcases/bad_feed.xml')
        with self.assertRaises(ValidationError) as cm:
            Feed.objects.create_from_feed(bad_feed, href="https://www.example.com/rss")
        self.assertEqual(cm.exception.code, 'invalid')


@all_requests
def relative_links_response(url, request):
    with open("feeds/tests/testcases/relative_links.xml", "rb") as f:
        return {'status_code': 200, 'content': f.read(), 'url': url}


class FeedManagerTests(TestCase):
    def test_get_feed(self):
        URL = 'http://example.com/feeds/all.atom.xml'
        LINK_URL = 'http://example.com/'
        with HTTMock(relative_links_response):
            feed = Feed.objects.get_feed(URL)
        self.assertEqual(feed.href, URL)
        self.assertEqual(feed.link, LINK_URL)
