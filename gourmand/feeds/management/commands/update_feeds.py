import socket

from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError

from feeds.models import Feed

TIMEOUT = 120
socket.setdefaulttimeout(TIMEOUT)


class Command(BaseCommand):
    help = "Check all existing feeds with subscriptions for updates"

    def handle(self, *args, **options):
        for feed in Feed.objects.filter(subscription__isnull=False):
            try:
                feed.update()
                for sub in feed.subscription_set.all():
                    sub.populate()
            except ValidationError as e:
                print(feed.href)
                print(e)
            except Exception as e:
                print(feed.href)
                raise e
