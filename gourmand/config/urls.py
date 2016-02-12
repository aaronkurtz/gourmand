from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

import debug_toolbar
import hijack.urls

import branding.urls
import subscriptions.urls

urlpatterns = [
    url(r'', include(branding.urls)),
    url(r'', include(subscriptions.urls)),
    url(r'^accounts/login/$', auth_views.login, name='login'),
    url(r'^accounts/logout/$', auth_views.logout, {'next_page': 'front'}, name='logout'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^hijack/', include(hijack.urls)),
    url(r'^__debug__/', include(debug_toolbar.urls)),
]
