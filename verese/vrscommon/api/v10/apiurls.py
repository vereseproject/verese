from django.conf.urls.defaults import patterns, include, url
from vrscommon.resource import Resource
from piston.authentication import HttpBasicAuthentication
from apiauth import DjangoAuthentication

from api import VeresedakiHandler, TransactionHandler, \
     RelationHandler, LoginHandler, LogoutHandler, \
     BalanceHandler

django_auth = DjangoAuthentication(login_url='/api/login/')
basic_auth = HttpBasicAuthentication(realm='verese')
veresedaki_handler = Resource(VeresedakiHandler, basic_auth)
transaction_handler = Resource(TransactionHandler, basic_auth)
relation_handler = Resource(RelationHandler, basic_auth)
login_handler = Resource(LoginHandler)
logout_handler = Resource(LogoutHandler)
balance_handler = Resource(BalanceHandler, django_auth)

urlpatterns = patterns(
    '',
    url(r'^relation/(?P<relation_id>\d+)/$', relation_handler),
    url(r'^transaction/(?P<group_veresedaki_id>\d+)/$', transaction_handler),
    url(r'^transaction/(?P<group_veresedaki_id>\d+)/add/$', veresedaki_handler),
    url(r'^transaction/$', transaction_handler),
    url(r'^veresedaki/(?P<veresedaki_id>\d+)/$', veresedaki_handler),
    url(r'^login/$', login_handler),
    url(r'^logout/$', logout_handler),
    url(r'^balance/overall/$', balance_handler, {'type':'overall'}),
    url(r'^balance/overall/detailed/$', balance_handler,
        {'type':'overall', 'detailed':True}),

    url(r'^balance/relation/list/$', balance_handler,
        {'type':'relation_list'}),
    url(r'^balance/relation/(?P<relation_id>\d+)/$', balance_handler,
        {'type': 'relation', 'detailed':False}),
    url(r'^balance/relation/(?P<relation_id>\d+)/detailed/$', balance_handler,
        {'type': 'relation', 'detailed':True}),
    url(r'^balance/currency/(?P<currency_code>\w+)/$', balance_handler,
        {'type':'currency', 'detailed':True}),
    url(r'^balance/currency/(?P<currency_code>\w+)/detailed/$', balance_handler,
        {'type':'currency', 'detailed':True}),

    )
