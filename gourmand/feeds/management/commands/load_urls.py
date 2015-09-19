import argparse

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

import feedparser

from feeds.models import Feed


class Command(BaseCommand):
    help = "Convert URLs pointing at RSS/Atom feeds to Feeds"

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='+', type=argparse.FileType('r'))

    def handle(self, *args, **options):
        for f in options['file']:
            for url in f.readlines():
                self.import_url(url)

    def import_url(self, url):
        url = url.strip()
        if Feed.objects.filter(href=url).exists():
            self.stderr.write("Feed already exists: {}".format(url))
            return
        parsed_feed = feedparser.parse(url)
        try:
            feed = Feed.objects.create_from_feed(parsed_feed)
        except ValidationError:
            self.stderr.write("Unable to load {}".format(url))
            return
        if Feed.objects.filter(href=feed.href).exists():
            self.stderr.write("Feed already exists: {}".format(feed.href))
            return
        feed.save()
