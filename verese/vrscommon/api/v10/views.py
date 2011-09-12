from piston.handler import PistonView, Field
import hashlib

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

class VeresedakiRelationView(PistonView):
    fields = [
        Field('ower', lambda x: x.email),
        'amount',
        'local_amount',
        'comment',
        'status',
        ]

class VeresedakiView(PistonView):
    fields = [
        Field('ower', lambda x: UserView(x), destination='ower'),
        'amount',
        'local_amount',
        'comment',
        'status',
        ]

class TransactionView(PistonView):
    fields = [
        'id',
        Field('payer', lambda x: UserView(x), destination='payer'),
        Field('veresedakia', lambda x: [VeresedakiView(y) for y in x]),
        'currency',
        'created',
        'comment',
        'status',
        Field('total_amount', destination='amount'),
        ]

class TransactionListView(PistonView):
    fields = [
        Field('',
              lambda x: [TransactionView(y) for y in x],
              destination='transactions'
              )
        ]
