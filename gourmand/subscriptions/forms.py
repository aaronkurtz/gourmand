from django import forms

from braces.forms import UserKwargModelFormMixin
import feedparser

from feeds.models import Feed, URL_MAX_LEN
from subscriptions.models import Subscription


class NewSubForm(UserKwargModelFormMixin, forms.Form):
    feed_url = forms.URLField(max_length=URL_MAX_LEN, label=('Feed URL'))

    def clean(self):
        cleaned_data = super(self.__class__, self).clean()
        url = cleaned_data['feed_url']
        if Subscription.objects.filter(owner=self.user, feed__href=url).exists():
            raise forms.ValidationError("You are already subscribed to %(url)s", code="already_subscribed", params={'url': url})
        if Feed.objects.filter(href=url).exists():
            cleaned_data['feed'] = Feed.objects.get(href=url)
            return cleaned_data
        fp = feedparser.parse(url)
        feed = Feed.objects.create_from_feed(fp)
        feed.save()
        cleaned_data['feed'] = feed
        return cleaned_data
