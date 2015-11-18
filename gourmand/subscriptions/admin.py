from django.contrib import admin
from .models import Subscription, PersonalArticle


@admin.register(Subscription)
class SubAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonalArticle)
class PersonalArticleAdmin(admin.ModelAdmin):
    pass
