from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^add/$', 'vrscommon.views.add', name="addpage"),
    url(r'^connections/$', 'vrscommon.views.connections', name="connectionspage"),
    url(r'^activity/$', 'vrscommon.views.activity', name="activitypage"),
    url(r'^dashboard/$', 'vrscommon.views.dashboard', name="dashboardpage"),

    )

