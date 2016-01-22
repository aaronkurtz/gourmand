from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

import branding.urls
import feeds.urls
import subscriptions.urls

urlpatterns = [
    url(r'', include(branding.urls)),
    url(r'', include(subscriptions.urls)),
    url(r'^accounts/login/$', auth_views.login, name='login'),
    url(r'^accounts/logout/$', auth_views.logout, {'next_page': 'front'}, name='logout'),
    url(r'^feeds/', include(feeds.urls)),
    url(r'^admin/', include(admin.site.urls)),
]
