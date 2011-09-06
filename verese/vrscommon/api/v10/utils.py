from django.conf.urls.defaults import url as django_url, patterns

def api_url(pattern, *args, **kwargs):
    assert pattern.endswith('$'), 'Api urls must be terminal.'
    pattern = r'%s(\.(?P<emitter_format>json|xml|jsonp)|(?<!.\.json|..\.xml|\.jsonp))$' % pattern[:-1]

    return django_url(pattern, *args, **kwargs)
