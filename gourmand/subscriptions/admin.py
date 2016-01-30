from django.contrib import admin
from django.template.loader import render_to_string

from .models import Subscription, PersonalArticle, Category


@admin.register(Subscription)
class SubAdmin(admin.ModelAdmin):
    list_display = ('owner', 'title', 'feed', 'category')
    list_display_links = ('feed',)
    select_related = ('feed', 'category')
    readonly_fields = ('owner', 'feed', 'category')
    fields = (('owner', 'feed'), 'category', 'title', 'public')
    search_fields = ('title', 'owner__username', 'feed__href')


@admin.register(PersonalArticle)
class PersonalArticleAdmin(admin.ModelAdmin):
    list_display = ('sub', 'article', 'active', 'archived')
    list_display_links = ('sub', 'article')
    select_related = ('sub', 'article')
    readonly_fields = ('sub', 'article')
    fields = ('sub', 'article', ('active', 'archived'))
    search_fields = ('sub__owner__username', 'sub__feed__href')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('owner', 'order', 'name')
    list_display_links = ('name',)
    readonly_fields = ('owner', 'show_subs')
    fields = ('owner', ('order', 'name'), 'show_subs')
    ordering = ('owner', '-order')
    search_fields = ('owner__username',)

    def show_subs(self, instance):
        qs = instance.subs.select_related('feed').order_by('title')
        return render_to_string('fragments/show_subs.html', {'subs': qs})
    show_subs.short_description = 'Subscriptions'
    show_subs.allow_tags = True
