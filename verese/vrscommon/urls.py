from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns(
    '',
    # url(r'^login$',
    #     'django.contrib.auth.views.login',
    #     {'template_name': 'verese.html'},
    #     name="login"),
    # url(r'^logout$',
    #     'django.contrib.auth.views.logout_then_login',
    #     name="logout"),
    url(r'^', 'vrscommon.views.main', name="vereseapp"),
    )

