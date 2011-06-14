from piston.handler import BaseHandler, AnonymousBaseHandler
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django import forms
from piston.decorator import decorator
from piston.utils import rc

from models import *
from exceptions import *

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
    def update(self, request):
        # user_id from request.user.id
        # user and userprofile updatesx
        pass

    @check_write_permission
    def delete(self, request):
        # user_id from request.user.id
        request.user.delete()
        return rc.DELETED

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
    def update(self, request, relation_id):
        relation = get_object_or_404(Relation, pk=relation_id)
        form = RelationUpdateForm(request.user, request.POST, instance=relation)

        if not form.is_valid():
            raise APIBadRequest(form.errors)

        form.save()
        return rc.ALL_OK

    @check_write_permission
    def delete(self, request, relation_id):
        obj = get_object_or_404(Relation, pk=relation_id)
        obj.delete()
        return rc.DELETED

class GroupVeresedakiHandler(BaseHandler):
    """
    GroupVeresedaki / Veresedaki Handler
    """
    model = GroupVeresedaki
    allowed_methods = ('GET', 'POST', 'DELETE')
    fields = ('id', 'payer', 'total_amount')

    # use formsets
    # https://docs.djangoproject.com/en/dev/topics/forms/formsets/#formset-validation

    @check_read_permission
    def read(self, request, group_veresedaki_id):
        # fetch group_veresedaki and related veresedakia
         return get_object_or_404(GroupVeresedaki, pk=group_veresedaki_id)

    @check_write_permission
    def create(self, request):
        # create group veresedaki
        # create veresedakia
        # return
        pass

    @check_write_permission
    def delete(self, request, group_veresedaki_id):
        # delete group veresedaki and veresedaki (auto)
        obj = get_object_or_404(GroupVeresedaki, pk=group_veresedaki_id)
        obj.delete()
        return rc.DELETED

class VeresedakiUpdateForm(forms.ModelForm):
    class Meta:
        model = Veresedaki
        fields = ('status', 'amount')

    def clean_status(self):
        return self.data.get('status', self.instance.status)

    def clean_amount(self):
        return self.data.get('amount', self.instance.amount)

class VeresedakiCreateForm(forms.ModelForm):
    class Meta:
        model = Veresedaki
        fields = ('ower', 'amount', 'comment')

class VeresedakiHandler(BaseHandler):
    """
    Veresedaki

    only create a veresedaki as part of a part veresedaki
    """
    model = Veresedaki
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

    @check_read_permission
    def read(self, request, veresedaki_id):
        return get_object_or_404(Veresedaki, pk=veresedaki_id)

    @check_write_permission
    def create(self, request, group_veresedaki_id):
        group_veresedaki = get_object_or_404(GroupVeresedaki,
                                             pk=group_veresedaki_id)
        form = VeresedakiCreateForm(request.POST,
                                    instance=Veresedaki(group=group_veresedaki)
                                    )
        if not form.is_valid():
            raise APIBadRequest(form.errors)

        form.save()
        return rc.CREATED


    @check_write_permission
    def update(self, request, veresedaki_id):
        # can update value
        # and / or set status
        veresedaki = get_object_or_404(Veresedaki, pk=veresedaki_id)

        form = VeresedakiUpdateForm(request.POST,
                                    instance=veresedaki
                                    )
        if not form.is_valid():
            raise APIBadRequest(form.errors)

        form.save()
        return rc.ALL_OK

    @check_write_permission
    def delete(self, request, veresedaki_id):
        obj = get_object_or_404(Veresedak, pk=veresedaki_id)
        obj.delete()
        return rc.DELETED

