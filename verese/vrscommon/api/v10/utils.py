from django.conf.urls.defaults import url as django_url, patterns

from piston import resource

def api_url(pattern, *args, **kwargs):
    assert pattern.endswith('$'), 'Api urls must be terminal.'
    pattern = r'%s(\.(?P<emitter_format>json|xml|jsonp)|(?<!.\.json|..\.xml|\.jsonp))$' % pattern[:-1]

    return django_url(pattern, *args, **kwargs)

class Resource(resource.Resource):
    def __init__(self, *args, **kwargs):
        if 'response_class' not in kwargs:
            kwargs['response_class'] = resource.EnhancedResponse

        super(Resource, self).__init__(*args, **kwargs)
