from django.conf.urls import url
from .views import FrontPage


urlpatterns = [
    url(r'^$', FrontPage.as_view(), name="front"),
]
