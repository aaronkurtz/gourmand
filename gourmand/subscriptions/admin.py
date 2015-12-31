from django.contrib import admin
from .models import Subscription, PersonalArticle, Category


@admin.register(Subscription)
class SubAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonalArticle)
class PersonalArticleAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass
