from django.db import models
from django.conf import settings

from feeds.models import Feed, Article


class Subscription(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    feed = models.ForeignKey(Feed)
    public = models.BooleanField(default=True)

    class Meta:
        unique_together = ('owner', 'feed')

    def __str__(self):
        return u"{}'s {}".format(self.owner, self.feed)


class PersonalArticle(models.Model):
    sub = models.ForeignKey(Subscription)
    article = models.ForeignKey(Article)
    active = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)

    class Meta:
        unique_together = ('sub', 'article')

    def __str__(self):
        return u"{}'s {}".format(self.sub.owner, self.article)
