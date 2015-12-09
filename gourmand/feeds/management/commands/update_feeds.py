from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError

from feeds.models import Feed


class Command(BaseCommand):
    help = "Check all existing feeds with subscriptions for updates"

    def handle(self, *args, **options):
        self.verbosity = options.get('verbosity')
        to_update_qs = Feed.objects.filter(subscription__isnull=False)
        update_len = to_update_qs.count()
        for idx, feed in enumerate(to_update_qs, 1):
            if self.verbosity > 1:
                print('{} of {}: Updating {} at {}'.format(idx, update_len, feed.title, feed.href))
            try:
                feed.update()
                for sub in feed.subscription_set.all():
                    sub.populate()
            except ValidationError as e:
                if self.verbosity:
                    print('Error updating {}: {}'.format(feed.href, e))
            except Exception as e:
                print('FATAL ERROR updating {}: {}'.format(feed.href, e))
                raise e
