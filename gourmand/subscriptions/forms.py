from django import forms

from braces.forms import UserKwargModelFormMixin
from defusedxml import DefusedXmlException
from defusedxml.cElementTree import fromstring

from feeds.models import Feed, URL_MAX_LEN
from subscriptions.models import Subscription, Category

MAX_OPML_FILE_SIZE = 1024 * 1024 * 2
OPML_CONTENT_TYPES = ('application/xml', 'text/xml', 'text/x-opml', 'text/x-opml+xml', 'application/xml+opml')
OPML_FILE_EXTS = ('xml', 'opml')


class NewSubForm(UserKwargModelFormMixin, forms.Form):
    feed_url = forms.URLField(max_length=URL_MAX_LEN, label=('Feed URL'))
    existing_category = forms.ModelChoiceField(required=False, queryset=Category.objects.none())
    new_category = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['existing_category'].queryset = Category.objects.filter(owner=self.user).exclude(name='Uncategorized').order_by('name')

    def clean_new_category(self):
        category = self.cleaned_data['new_category']
        if category and Category.objects.filter(owner=self.user, name=category).exists():
            raise forms.ValidationError("You already have a category named %(name)s", code="category_exists", params={'name': category})
        return category

    def clean(self):
        if 'feed_url' not in self.cleaned_data:
            return self.cleaned_data
        cleaned_data = super().clean()
        url = cleaned_data['feed_url']
        if Subscription.objects.filter(owner=self.user, feed__href=url).exists():
            raise forms.ValidationError("You are already subscribed to %(url)s", code="already_subscribed", params={'url': url})
        feed = Feed.objects.get_feed(url)
        if feed.href != url:
            if Subscription.objects.filter(owner=self.user, feed__href=feed.href).exists():
                raise forms.ValidationError("You are already subscribed to %(url)s", code="already_subscribed", params={'url': feed.href})
        cleaned_data['feed'] = feed
        existing_category = cleaned_data['existing_category']
        new_category = cleaned_data['new_category']
        if existing_category and new_category:
            raise forms.ValidationError("You can't add a new category and pick an existing one.", code="new_and_existing_categories")
        return cleaned_data


class UpdateSubscriptionForm(UserKwargModelFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(owner=self.user).order_by('name')
        self.fields['category'].empty_label = None

    class Meta:
        model = Subscription
        fields = ('title', 'category', 'public')
        widgets = {'title': forms.TextInput}


class ImportOPMLForm(UserKwargModelFormMixin, forms.Form):
    opml_file = forms.FileField(label='OPML File')
    mark_read = forms.BooleanField(required=False, label='Mark posts as read')

    def clean(self):
        if 'opml_file' not in self.cleaned_data:
            return self.cleaned_data
        cleaned_data = super().clean()
        opml_file = cleaned_data['opml_file']
        if opml_file.size > MAX_OPML_FILE_SIZE:
            raise forms.ValidationError('Your OPML file was too large: %(size)s', code="too_large", params={'size': opml_file.size})
        if opml_file.content_type not in OPML_CONTENT_TYPES:
            raise forms.ValidationError('The file was not a valid OPML file: %(content_type)s',
                                        code="invalid", params={'content_type': opml_file.content_type})
        opml_contents = opml_file.read()
        try:
            opml = fromstring(opml_contents, forbid_dtd=True)
            feeds = opml.findall('./body//outline[@xmlUrl]')
            if not feeds:
                raise forms.ValidationError('No feeds were found in the OPML file', code="no_feeds")
        except DefusedXmlException:
            raise forms.ValidationError('The file was not a valid OPML file', code="invalid")
        # Use SyntaxError, as ParseError doesn't work here
        except SyntaxError:
            raise forms.ValidationError('The file was not a valid OPML file', code="invalid")
        cleaned_data['feeds'] = feeds
        return cleaned_data
