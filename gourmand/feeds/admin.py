from django.contrib import admin
from .models import Feed, Article


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('title', 'href', 'link')
    list_display_links = ('title', 'href')
    search_fields = ('title', 'href')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('feed', 'gid', 'title', 'when')
    list_display_links = ('gid',)
    search_fields = ('feed__title', 'feed__href')
