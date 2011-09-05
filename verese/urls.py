from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
import vrscommon

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'verese.views.home', name='home'),
    # url(r'^verese/', include('verese.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1.0/', include('verese.vrscommon.api.v10.apiurls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout' ),

)

if settings.LOCAL_DEVELOPMENT:
    urlpatterns += patterns("django.views",
        url(r"%s(?P<path>.*)$" % settings.MEDIA_URL[1:],
            "static.serve", {"document_root": settings.MEDIA_ROOT,}),
	url(r'^dev/(?P<path>.*)$', "static.serve", {"document_root":"vrscommon/templates"})
    )
