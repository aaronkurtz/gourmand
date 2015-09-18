from django.core.exceptions import ValidationError
from django.test import TestCase

import feedparser

from feeds.models import Feed


class FeedTests(TestCase):
    def test_can_create_from_good(self):
        valid_feed = feedparser.parse('feeds/tests/atom_feed.xml')
        with self.assertRaises(ValidationError):
            Feed.objects.create_from_feed(valid_feed)
        feed = Feed.objects.create_from_feed(valid_feed, href="https://www.comic-rocket.com/explore/ow-my-sanity/rss")
        self.assertEqual(feed.title, "Ow My Sanity")
        self.assertEqual(feed.link, "https://www.comic-rocket.com/explore/ow-my-sanity/")
        self.assertEqual(feed.href, "https://www.comic-rocket.com/explore/ow-my-sanity/rss")
        self.assertEqual(str(feed), feed.title)

    def test_can_create_from_bad(self):
        bad_feed = feedparser.parse('feeds/tests/bad_feed.xml')
        with self.assertRaises(ValidationError):
            Feed.objects.create_from_feed(bad_feed)
