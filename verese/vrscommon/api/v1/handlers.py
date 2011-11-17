from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import get_object_or_404
from django.forms.models import inlineformset_factory
from django.db import transaction

from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.decorator import decorator
from piston.utils import rc
from piston.resource import PistonBadRequestException,\
     PistonForbiddenException, PistonNotFoundException

from vrscommon.models import *
from vrscommon.exceptions import *
from forms import *
from views import *

def validate(v_form, operations):
    # We don't use piston.utils.validate function
    # because it does not support request.FILES
    # and it's not according to documentation
    # i.e. when a form is valid it does not populate
    # request.form
    @decorator
    def wrap(function, self, request, *args, **kwargs):
        form = v_form(*tuple( getattr(request, operation) for operation in operations),
                      **{'request':request}
                      )

        if form.is_valid():
            request.form = form
            return function(self, request, *args, **kwargs)
        else:
            raise FormValidationError(form)

    return wrap

class CurrencyHandler(BaseHandler):
    """
    Return list of supported currencies
    """
    allowed_methods = ('GET', )
    model = Currency

    def read(self, request):
        return CurrencyListView(Currency.objects.all())

class BalanceHandler(BaseHandler):
    """
    User balance handler
    """
    allowed_methods = ('GET', )

    def read(self, request):
        user_profile = request.user.get_profile()
        return BalanceView(user_profile)


class LoginHandler(BaseHandler):
    """
    User login
    """
    allowed_methods = ('POST', )

    def create(self, request):
        """
        Create a new session
        """
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return rc.ALL_OK
            else:
                rc.FORBIDDEN
        else:
            return rc.FORBIDDEN

class LogoutHandler(BaseHandler):
    """
    User logout
    """
    allowed_methods = ('GET', )

    def read(self, request):
        """
        Logout user
        """
        auth.logout(request)
        return rc.ALL_OK

class AnonymousUserHandler(AnonymousBaseHandler):
    """
    User registration
    """
    model = User
    allowed_methods = ('POST', )

    def create(self, request):
        pass

class UserHandler(BaseHandler):
    """
    User  delete, view and update information
    """
    model = User
    allowed_methods = ('GET', 'PUT', 'DELETE')
    fields = ('first_name',
              'last_name',
              'username',
              'email',
              )

    def read(self, request):
        return UserView(request.user)

    @transaction.commit_on_success()
    def update(self, request):
        # user_id from request.user.id
        # user and userprofile updates
        form = UserUpdateForm(request.POST, instance=request.user)

        if not form.is_valid():
            raise APIBadRequest(form.errors)

        form.save()

        if form.cleaned_data.get('currency', None):
            profile = request.user.get_profile()
            profile.currency = form.cleaned_data.get('currency')
            profile.save()

        return rc.ALL_OK

    @transaction.commit_on_success()
    def delete(self, request):
        # user_id from request.user.id
        request.user.delete()
        return rc.DELETED

class RelationHandler(BaseHandler):
    """
    Get / update relation information
    Relations are automatically created on new veredakia
    """
    model = Relation
    allowed_methods = ('GET', 'PUT', 'DELETE')

    def read(self, request, relation_id=None, details=False):
        if relation_id:
            try:
                relation = Relation.objects.\
                           get((Q(user1=request.user)|Q(user2=request.user)),
                               pk=relation_id
                               )

            except Relation.DoesNotExist:
                return rc.FORBIDDEN

            if details:
                return RelationDetailedView(relation)

            else:
                return RelationView(relation)

        else:
            relations = Relation.objects.\
                        filter(Q(user1=request.user)|Q(user2=request.user))

            return RelationListView(relations)

    @transaction.commit_on_success()
    def update(self, request, relation_id):
        relation = get_object_or_404(Relation, pk=relation_id)
        form = RelationUpdateForm(request.user, request.POST, instance=relation)

        if not form.is_valid():
            raise APIBadRequest(form.errors)

        form.save()
        return rc.ALL_OK

    @transaction.commit_on_success()
    def delete(self, request, relation_id):
        obj = get_object_or_404(Relation, pk=relation_id)
        obj.delete()
        return rc.DELETED

class TransactionHandler(BaseHandler):
    """
    Transaction / Veresedaki Handler
    """
    allowed_methods = ('GET', 'POST', 'DELETE')
    fields = ('id', 'payer', 'total_amount')

    # use formsets
    # https://docs.djangoproject.com/en/dev/topics/forms/formsets/#formset-validation

    def read(self, request, transaction_id=None):
        # fetch transaction and related veresedakia
        if transaction_id:
            try:
                transaction = Transaction.objects.\
                              get(Q(payer=request.user) |\
                                  Q(veresedaki__ower__in=[request.user]),
                                  id=transaction_id,
                                  )

            except Transaction.DoesNotExist:
                return rc.FORBIDDEN

            return TransactionView(transaction)

        else:
            transactions = Transaction.objects.\
                           filter(Q(payer=request.user)|\
                                  Q(veresedaki__ower__in = [request.user]
                                    )
                                  ).distinct()

            return TransactionListView(transactions)

    @transaction.commit_on_success()
    def create(self, request):
        form = TransactionCreateForm(request.POST,
                                         instance=Transaction(payer=request.user)
                                         )
        if not form.is_valid():
            raise APIBadRequest(form.errors)

        form.save()

        veresedaki_formset = inlineformset_factory(Transaction, Veresedaki)
        formset = veresedaki_formset(request.POST, instance=form.instance)
        if not formset.is_valid():
            raise APIBadRequest(formset.errors)

        formset.save()

        return rc.CREATED

    @transaction.commit_on_success()
    def delete(self, request, transaction_id):
        # delete transaction and veresedaki (auto)
        obj = get_object_or_404(Transaction, pk=transaction_id)
        obj.delete()
        return rc.DELETED


class VeresedakiHandler(BaseHandler):
    """
    Veresedaki Handler
    """
    allowed_methods = ('PUT', )

    # use formsets
    # https://docs.djangoproject.com/en/dev/topics/forms/formsets/#formset-validation

    @transaction.commit_on_success()
    def update(self, request, veresedaki_id, action):
        veresedaki = get_object_or_404(Veresedaki, pk=veresedaki_id)

        # check if user exists in transaction
        # TODO add transaction payer
        if not veresedaki.ower == request.user:
            raise APIForbidden("You are not the ower")


        for status in status_choices:
            if status[1].lower() == action:
                action = status[0]
                break

        if not isinstance(action, int):
            raise PistonBadRequestException("Invalid action")

        elif veresedaki.status.status == action:
            raise rc.DUPLICATE_ENTRY

        status = VeresedakiStatus(user=request.user,
                                  veresedaki=veresedaki,
                                  status=action)
        status.save()

        return rc.ALL_OK
