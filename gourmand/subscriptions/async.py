from collections import Counter
import time

from django.core.exceptions import ValidationError
from django.template.defaultfilters import pluralize

from async_messages import messages as async_messages
from django_q.humanhash import uuid
from django_q.tasks import result_group, async, count_group, delete_group
from django_q.conf import logger

from feeds.models import Feed
from .models import Subscription, Category

IMPORT_WAIT = 2 * 60


def import_urls(user, fresh_urls, mark_read):
    group = uuid()
    size = len(fresh_urls)
    for url in fresh_urls:
        async(subscribe_to_imported_url, user, url, mark_read, group=group)
    start = time.time()
    while True:
        # print("Time", time.time() - start, "count", count_group(group))
        if (time.time() - start) > IMPORT_WAIT:
            # print("TIME!")
            break
        if count_group(group) == size:
            # print("COUNT!")
            break
        time.sleep(1)
    import_results = Counter(result_group(group))
    pretty_results = ', '.join("{}: {}".format(*x) for x in import_results.items())
    num_added = import_results['added']
    num_existed = import_results['existed']
    num_errors = import_results['error']
    if num_added:
        async_messages.success(user, "Import complete - you subscribed to {sub} feed{s}.".format(sub=num_added, s=pluralize(num_added)))
    else:
        async_messages.info(user, "Import complete - no new subscriptions were added.")
    if num_existed:
        async_messages.info(user,
                            "You were already subscribed to {sub_exists} imported feed{s}.".format(sub_exists=num_existed, s=pluralize(num_existed)))
    if num_errors:
        async_messages.error(user, "There was an error subscribing to {errors} imported feed{s}.".format(errors=num_errors, s=pluralize(num_errors)))
    logger.info('User %(user)s OPML import complete - %(results)s', {'user': user, 'results': pretty_results})
    delete_group(group, tasks=True)
    return pretty_results


def subscribe_to_imported_url(user, url, mark_read):
    try:
        feed = Feed.objects.get_feed(url)
        category = Category.objects.get_user_categories(user).get(name="Uncategorized")
        sub, created = Subscription.objects.get_or_create(owner=user, feed=feed, title=feed.title, category=category)
        if created:
            sub.populate()
            if mark_read:
                sub.personalarticle_set.update(active=False)
            return('added')
        else:
            return('existed')
    except ValidationError:
        return('error')
