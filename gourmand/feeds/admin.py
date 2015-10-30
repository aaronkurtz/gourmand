from django.contrib import admin
from .models import Feed, Article


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    pass


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass
