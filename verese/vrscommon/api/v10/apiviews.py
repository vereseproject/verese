from piston.handler import PistonView, Field

class BalanceView(PistonView):
    fields = [
        'id',
        'balance',
        ]
