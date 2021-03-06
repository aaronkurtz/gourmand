from django.db import models
from django.conf import settings

from feeds.models import Feed, Article


class CategoryManager(models.Manager):
    def get_user_categories(self, user):
        categories = super().get_queryset().filter(owner=user)
        if categories:
            return categories
        else:
            Category.objects.create(owner=user, order=0, name="Uncategorized")
            return super().get_queryset().filter(owner=user)


class Category(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    order = models.PositiveSmallIntegerField()
    shared = models.BooleanField(default=False)
    name = models.TextField()

    objects = CategoryManager()

    class Meta:
        unique_together = (('owner', 'name'), ('owner', 'order'))
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Subscription(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    feed = models.ForeignKey(Feed)
    category = models.ForeignKey(Category, related_name='subs')
    title = models.TextField()

    class Meta:
        unique_together = ('owner', 'feed')

    def __str__(self):
        return u"{}'s {}".format(self.owner, self.title)

    def populate(self):
        new_articles = self.feed.article_set.exclude(personalarticle__sub=self)
        PersonalArticle.objects.bulk_create([PersonalArticle(sub=self, article=article) for article in new_articles])


class PersonalArticle(models.Model):
    sub = models.ForeignKey(Subscription)
    article = models.ForeignKey(Article)
    active = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)

    class Meta:
        unique_together = ('sub', 'article')

    def __str__(self):
        return u"{}'s {}".format(self.sub.owner, self.article)
