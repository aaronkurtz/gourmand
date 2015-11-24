from django.conf.urls import include, url
from django.contrib import admin

import feeds.urls
import subscriptions.urls

urlpatterns = [
    url(r'', include(subscriptions.urls)),
    url(r'^feeds/', include(feeds.urls)),
    url(r'^admin/', include(admin.site.urls)),
]
