import hashlib
from datetime import datetime

from piston.handler import PistonView, Field

class CurrencyListView(PistonView):
    fields = [
        Field('', lambda x: x, destination='currencies')
        ]

class CurrencyView(PistonView):
    fields = [
        'currency',
        'balance',
        ]

class BalanceApproximationView(PistonView):
    fields = [
        'currency',
        'balance',
        ]

class BalanceView(PistonView):
    fields = [
        Field('',
              lambda x: BalanceApproximationView(x),
              destination='balance_aggregation'
              ),
        Field('balance_detailed',
              lambda x: [y for y in x],
              destination='balance_details'
              ),
        ]

class RelationDetailedView(PistonView):
    fields = [
        'id',
        'balance',
        'currency',
        Field('user1', lambda x: UserView(x), destination='user1'),
        Field('user2', lambda x: UserView(x), destination='user2'),
        Field('',
              lambda x: [VeresedakiRelationView(y) for y in x.get_veresedakia()],
              destination='veresedakia'
              )
        ]

class UserView(PistonView):
    fields = [
        'first_name',
        'last_name',
        'username',
        'email',
        Field('email',
              lambda x: hashlib.md5(x).hexdigest(),
              destination="emailmd5"
              ),
        ]


class RelationView(PistonView):
    fields = [
        'id',
        'balance',
        'currency',
        Field('created', lambda x: x.strftime("%Y-%m-%dT%H:%M:%S")),
        Field('updated', lambda x: x.strftime("%Y-%m-%dT%H:%M:%S")),
        Field('user1', lambda x: UserView(x), destination='user1'),
        Field('user2', lambda x: UserView(x), destination='user2'),
        ]

class RelationListView(PistonView):
    fields = [
        Field('',
              lambda x: [RelationView(y) for y in x],
              destination='relations'
              )
        ]

class StatusView(PistonView):
    fields = [
        'status',
        Field('user', lambda x: UserView(x)),
        Field('created', lambda x: x.strftime("%Y-%m-%dT%H:%M:%S")),
        ]

class VeresedakiRelationView(PistonView):
    fields = [
        Field('ower', lambda x: x.email),
        'amount',
        'local_amount',
        'comment',
        Field('status', lambda x: StatusView(x))
        ]

class VeresedakiView(PistonView):
    fields = [
        Field('ower', lambda x: UserView(x)),
        'amount',
        'local_amount',
        'comment',
        Field('status', lambda x: StatusView(x))
        ]

class TransactionView(PistonView):
    fields = [
        'id',
        Field('payer', lambda x: UserView(x), destination='payer'),
        Field('veresedakia', lambda x: [VeresedakiView(y) for y in x]),
        'currency',
        Field('created', lambda x: x.strftime("%Y-%m-%dT%H:%M:%S")),
        'comment',
        'status',
        'lat',
        'lon',
        'place',
        Field('total_amount', destination='amount'),
        ]

class TransactionListView(PistonView):
    fields = [
        Field('',
              lambda x: [TransactionView(y) for y in x],
              destination='transactions'
              )
        ]

class PendingView(PistonView):
    fields = [
        Field('transaction', lambda x: TransactionView(x), destination='')
        ]

class PendingListView(PistonView):
    fields = [
        Field('',
              lambda x: [PendingView(y) for y in x],
              destination='pending'
              )
        ]
