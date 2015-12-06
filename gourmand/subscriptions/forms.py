from django import forms

from braces.forms import UserKwargModelFormMixin
from defusedxml import DefusedXmlException
from defusedxml.cElementTree import fromstring
import feedparser

from feeds.models import Feed, URL_MAX_LEN
from subscriptions.models import Subscription

MAX_OPML_FILE_SIZE = 1024 * 1024 * 2
OPML_CONTENT_TYPES = ('application/xml', 'text/xml', 'text/x-opml', 'text/x-opml+xml')
OPML_FILE_EXTS = ('xml', 'opml')


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
        feed.update(fp)
        cleaned_data['feed'] = feed
        return cleaned_data


class ImportOPMLForm(UserKwargModelFormMixin, forms.Form):
    opml_file = forms.FileField(label='OPML File')

    def clean(self):
        cleaned_data = super(self.__class__, self).clean()
        opml_file = cleaned_data['opml_file']
        if opml_file.size > MAX_OPML_FILE_SIZE:
            raise forms.ValidationError('Your OPML file was too large: %(size)s', code="too_large", params={'size': opml_file.size})
        if opml_file.content_type not in OPML_CONTENT_TYPES:
            raise forms.ValidationError('The file was not a valid OPML file: %(content_type)s',
                                        code="invalid", params={'content_type': opml_file.content_type})
        opml_contents = opml_file.read()
        try:
            opml = fromstring(opml_contents, forbid_dtd=True)
            feeds = opml.findall('./body/outline')
            if not feeds:
                raise forms.ValidationError('No feeds were found in the OPML file', code="no_feeds")
        except DefusedXmlException:
            raise forms.ValidationError('The file was not a valid OPML file', code="invalid")
        # Use SyntaxError, as ParseError doesn't work here
        except SyntaxError:
            raise forms.ValidationError('The file was not a valid OPML file', code="invalid")
        cleaned_data['feeds'] = feeds
        return cleaned_data
