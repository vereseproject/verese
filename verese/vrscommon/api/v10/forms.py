from django import forms
from django.contrib.auth.models import User

from vrscommon.models import *

class RelationUpdateForm(forms.ModelForm):
    class Meta:
        model = Relation
        fields = ('balance', 'user1_trust_limit', 'user2_trust_limit')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(RelationUpdateForm, self).__init__(*args, **kwargs)

    def clean_user1_trust_limit(self):
        if self.user == self.instance.user1:
            return self.date.get('user1_trust_limit',
                                 self.instance.user1_trust_limit)
        else:
            return self.instance.user1_trust_limit

    def clean_user2_trust_limit(self):
        if self.user == self.instance.user2:
            return self.date.get('user2_trust_limit',
                                 self.instance.user1_trust_limit)
        else:
            return self.instance.user2_trust_limit

class VeresedakiUpdateForm(forms.ModelForm):
    status = forms.ChoiceField(choices=status_choices)

    def __init__(self, user, *args, **kwargs):
        self._user = user
        super(VeresedakiUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Veresedaki
        fields = ('status', 'amount')

    def clean_status(self):
        if self.data.get('status', None):
            # user is changing status, create a new VeresedakiStatus
            status = VeresedakiStatus(user=self._user,
                                      status=int(self.data.get('status'))
                                      )
            status.save()
            return status

        else:
            return self.instance.status

    def clean_amount(self):
        return self.data.get('amount', self.instance.amount)

class VeresedakiCreateForm(forms.ModelForm):
    class Meta:
        model = Veresedaki
        fields = ('ower', 'transaction', 'amount', 'comment')


class TransactionCreateForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('comment', 'currency')
        # TODO add tags

class UserUpdateForm(forms.ModelForm):
    currency = forms.IntegerField(required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def clean_currency(self):
        if self.data.get('currency', None):
            try:
                currency = Currency.objects.get(pk=self.data['currency'])
            except Currency.DoesNotExist:
                raise FormValidationError('Currency does not exist')

            return currency

    def clean_first_name(self):
        if self.data.get('first_name', None):
            return self.data['first_name']

        else:
            return self.instance.first_name

    def clean_last_name(self):
        if self.data.get('last_name', None):
            return self.data['last_name']

        else:
            return self.instance.last_name
