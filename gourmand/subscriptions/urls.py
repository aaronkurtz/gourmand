from django.conf.urls import url
from .views import FrontPage, Reader, PersonalArticleList


urlpatterns = [
    url(r'^$', FrontPage.as_view(), name="front"),
    url(r'^reader/$', Reader.as_view(), name="reader"),
    url(r'^reader/(?P<pk>[0-9]+)/$', PersonalArticleList.as_view(), name="subscription"),
]
