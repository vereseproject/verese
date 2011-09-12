from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns(
    'vrscommon.views',
    url(r'^$', 'main'),
    url(r'^welcome/$', 'welcome'),
    )

