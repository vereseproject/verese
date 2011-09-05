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
              destination='balance_approximation'
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
        'user1',
        'user2',
        Field('',
              lambda x: [VeresedakiRelationView(y) for y in x.get_veresedakia()],
              destination='veresedakia'
              )
        ]

class RelationView(PistonView):
    fields = [
        'id',
        'balance',
        'currency',
        'user1',
        'user2',
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
        'ower',
        'amount',
        'local_amount',
        'comment',
        'status',
        ]

class TransactionDetailedView(PistonView):
    fields = [
        'id',
        'balance',
        'currency',
        'user1',
        'user2',
        Field('',
              lambda x: [VeresedakiRelationView(y) for y in x.get_veresedakia()],
              destination='veresedakia'
              )
        ]

class TransactionView(PistonView):
    fields = [
        'id',
        'payer',
        Field('veresedakia', lambda x: [VeresedakiView(y) for y in x]),
        'currency',
        'created',
        'comment',
        'status',
        ]

class TransactionListView(PistonView):
    fields = [
        Field('',
              lambda x: [TransactionView(y) for y in x],
              destination='transactions'
              )
        ]
