from django.conf.urls.defaults import patterns, include, url
from resource import Resource
from piston.authentication import HttpBasicAuthentication

from api import VeresedakiHandler, GroupVeresedakiHandler, \
     RelationHandler

basic_auth = HttpBasicAuthentication(realm='verese')
veresedaki_handler = Resource(VeresedakiHandler)
group_veresedaki_handler = Resource(GroupVeresedakiHandler)
relation_handler = Resource(RelationHandler, basic_auth)

urlpatterns = patterns(
    '',
    (r'^relation/(?P<relation_id>\d+)/$', relation_handler),
    (r'^groupveresedaki/(?P<group_veresedaki_id>\d+)/$', group_veresedaki_handler),
    (r'^groupveresedaki/(?P<group_veresedaki_id>\d+)/add/$', veresedaki_handler),
    (r'^veresedaki/(?P<veresedaki_id>\d+)/$', veresedaki_handler),
    )


