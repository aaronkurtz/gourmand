from django.contrib import admin
from .models import Feed, Article, ExtraContent, ExtraLink


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('title', 'href', 'link')
    list_display_links = ('title', 'href')
    search_fields = ('title', 'href')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('feed', 'gid', 'title', 'when')
    list_display_links = ('gid',)
    readonly_fields = ('feed', 'gid', 'when')
    fields = (('feed', 'gid'), 'when', 'title', 'main_link', 'main_content')
    search_fields = ('feed__title', 'feed__href')


@admin.register(ExtraContent)
class ExtraContent(admin.ModelAdmin):
    list_display = ('article',)
    search_fields = ('feed__title', 'feed__href')
    readonly_fields = ('article',)
    fields = ('article', 'content')


@admin.register(ExtraLink)
class ExtraLink(admin.ModelAdmin):
    list_display = ('article', 'link', 'title')
    search_fields = ('feed__title', 'feed__href')
    readonly_fields = ('article',)
    fields = ('article', 'title', 'link')
