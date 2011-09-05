from piston.handler import BaseHandler, AnonymousBaseHandler
from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import get_object_or_404
from django.forms.models import inlineformset_factory
from django.db import transaction

from piston.decorator import decorator
from piston.utils import rc

from vrscommon.models import *
from exceptions import *
from apiforms import *

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

@decorator
def check_read_permission(function, self, request, *args, **kwargs):
    return function(self, request, *args, **kwargs)

@decorator
def check_write_permission(function, self, request, *args, **kwargs):
    return function(self, request, *args, **kwargs)

class BalanceHandler(BaseHandler):
    """
    User balance handler
    """
    allowed_methods = ('GET', )

    def read(self, request, type, *args, **kwargs):
        user_profile = request.user.get_profile()

        if type == 'overall':
            if kwargs.get('detailed', False):
                return user_profile.balance

            else:
                return user_profile.balance_detailed

        elif type == 'relation_list':
            return 'relation_list'

        elif type == 'relation':
            return 'relation'

        elif type == 'currency':
            pass


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

    @check_read_permission
    def read(self, request):
        return request.user.id

    @check_write_permission
    @transaction.commit_on_success()
    def update(self, request):
        # user_id from request.user.id
        # user and userprofile updatesx
        pass

    @check_write_permission
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

    @check_read_permission
    def read(self, request, relation_id):
        return get_object_or_404(Relation, pk=relation_id)

    @check_write_permission
    @transaction.commit_on_success()
    def update(self, request, relation_id):
        relation = get_object_or_404(Relation, pk=relation_id)
        form = RelationUpdateForm(request.user, request.POST, instance=relation)

        if not form.is_valid():
            raise APIBadRequest(form.errors)

        form.save()
        return rc.ALL_OK

    @check_write_permission
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

    @check_read_permission
    def read(self, request, group_veresedaki_id):
        # fetch group_veresedaki and related veresedakia
         return get_object_or_404(Transaction, pk=group_veresedaki_id)

    @check_write_permission
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

    @check_write_permission
    @transaction.commit_on_success()
    def delete(self, request, group_veresedaki_id):
        # delete group veresedaki and veresedaki (auto)
        obj = get_object_or_404(Transaction, pk=group_veresedaki_id)
        obj.delete()
        return rc.DELETED


class VeresedakiHandler(BaseHandler):
    """
    Veresedaki

    only create a veresedaki as part of a group veresedaki
    """
    model = Veresedaki
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

    @check_read_permission
    def read(self, request, veresedaki_id):
        return get_object_or_404(Veresedaki, pk=veresedaki_id)

    @check_write_permission
    @transaction.commit_on_success()
    def create(self, request, group_veresedaki_id):
        group_veresedaki = get_object_or_404(Transaction,
                                             pk=group_veresedaki_id)

        data = request.POST
        data['group'] = group_veresedaki_id
        form = VeresedakiCreateForm(data,
                                    instance=Veresedaki(group=group_veresedaki)
                                    )

        if not form.is_valid():
            raise APIBadRequest(form.errors)

        form.save()
        return rc.CREATED

    @check_write_permission
    @transaction.commit_on_success()
    def update(self, request, veresedaki_id):
        # can update value
        # and / or set status
        veresedaki = get_object_or_404(Veresedaki, pk=veresedaki_id)

        form = VeresedakiUpdateForm(request.user,
                                    request.POST,
                                    instance=veresedaki,
                                    )
        if not form.is_valid():
            raise APIBadRequest(form.errors)

        form.save()
        return rc.ALL_OK

    @check_write_permission
    @transaction.commit_on_success()
    def delete(self, request, veresedaki_id):
        obj = get_object_or_404(Veresedak, pk=veresedaki_id)
        obj.delete()
        return rc.DELETED

