from django.conf.urls import url
from .views import FrontPage, Reader, PersonalArticleList, AddSubscription
from .views import ReadNew, ArticleReader
from .views import ImportOPML, ExportOPML


urlpatterns = [
    url(r'^$', FrontPage.as_view(), name="front"),
    url(r'^reader/$', Reader.as_view(), name="reader"),
    url(r'^reader/add$', AddSubscription.as_view(), name="add_subscription"),
    url(r'^reader/opml/import$', ImportOPML.as_view(), name="import_opml"),
    url(r'^reader/opml/export$', ExportOPML.as_view(), name="export_opml"),
    url(r'^reader/(?P<pk>[0-9]+)/$', PersonalArticleList.as_view(), name="subscription"),
    url(r'^reader/(?P<pk>[0-9]+)/read_new$', ReadNew.as_view(), name="read_new"),
    url(r'^articles/(?P<pk>[0-9]+)/$', ArticleReader.as_view(), name="article"),
]
