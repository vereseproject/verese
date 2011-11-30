import urllib
import json

from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import get_object_or_404
from django.forms.models import inlineformset_factory
from django.db import transaction

from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.decorator import decorator
from piston.utils import rc, FormValidationError
from piston.resource import PistonBadRequestException,\
     PistonForbiddenException, PistonNotFoundException

from vrscommon.models import *
from forms import *
from views import *

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
            raise FormValidationError(form)

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

    def read(self, request, relation_id=None, details=False, short=False):
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

            if short:
                userlist = []
                print relations
                for relation in relations:
                    userlist.append(relation.user1)
                    userlist.append(relation.user2)

                userlist = set(userlist)
                userlist.discard(request.user)

                return RelationListShortView(userlist)

            return RelationListView(relations)

    @transaction.commit_on_success()
    def update(self, request, relation_id):
        relation = get_object_or_404(Relation, pk=relation_id)
        form = RelationUpdateForm(request.user, request.POST, instance=relation)

        if not form.is_valid():
            raise FormValidationError(form)

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

    def read(self, request, transaction_id=None, before=False, after=False):
        limit = request.GET.get('limit', 10)

        # fetch transaction and related veresedakia
        if transaction_id:
            if before == False and after == False:
                try:
                    transaction = Transaction.objects.\
                                  get(Q(payer=request.user) |\
                                      Q(veresedaki__ower__in=[request.user]),
                                      id=transaction_id,
                                      )

                except Transaction.DoesNotExist:
                    return rc.FORBIDDEN

                return TransactionView(transaction)

            elif before:
                # return objects with id smaller than transaction_id
                transactions = Transaction.objects.\
                               filter(Q(payer=request.user)|\
                                      Q(veresedaki__ower__in = [request.user]
                                        )
                                      ).distinct().filter(id__lt=transaction_id)\
                                      [:limit]

                return TransactionListView(transactions)

            elif after:
                # return objects with id larger than transaction_id
                transactions = Transaction.objects.\
                               filter(Q(payer=request.user)|\
                                      Q(veresedaki__ower__in = [request.user]
                                        )
                                      ).distinct().filter(id__gt=transaction_id)\
                                      [:limit]

                return TransactionListView(transactions)

        else:
            transactions = Transaction.objects.\
                           filter(Q(payer=request.user)|\
                                  Q(veresedaki__ower__in = [request.user]
                                    )
                                  ).distinct()[:limit]

            return TransactionListView(transactions)

    # use formsets
    # https://docs.djangoproject.com/en/dev/topics/forms/formsets/#formset-validation
    @transaction.commit_on_success()
    def create(self, request):
        form = TransactionCreateForm(request.POST,
                                     instance=Transaction(payer=request.user)
                                     )

        if not form.is_valid():
            raise FormValidationError(form)

        form.save()

        veresedaki_formset = inlineformset_factory(Transaction, Veresedaki)
        formset = veresedaki_formset(request.POST, instance=form.instance)
        if not formset.is_valid():
            raise FormValidationError(formset)

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
    update_choices = {'accept':40, 'cancel':10, 'deny':20}

    # use formsets
    # https://docs.djangoproject.com/en/dev/topics/forms/formsets/#formset-validation

    @transaction.commit_on_success()
    def update(self, request, veresedaki_id, action):
        veresedaki = get_object_or_404(Veresedaki, pk=veresedaki_id)

        try:
            status = self.update_choices[action]

        except KeyError:
            raise PistonBadRequestException("Invalid action")

        if veresedaki.status.status == status:
            raise rc.DUPLICATE_ENTRY

        # permission control
        if action == 'accept' and not request.user == veresedaki.ower:
            raise PistonForbiddenException("You are not allowed to accept this veresedaki")

        elif action == 'deny' and not request.user == veresedaki.ower:
            raise PistonForbiddenException("You are not allowed to deny this veresedaki")

        elif action == 'cancel' and not request.user == veresedaki.transaction.payer:
            raise PistonForbiddenException("You are not allowed to cancel this veresedaki")

        status = VeresedakiStatus(user=request.user,
                                  veresedaki=veresedaki,
                                  status=status)
        status.save()

        return rc.ALL_OK

class PendingHandler(BaseHandler):
    """
    Pending Handler returns transaction that need user's action
    """
    allowed_methods = ('GET',)

    def read(self, request):
        query = Veresedaki.objects.\
                filter(Q(ower=request.user) |\
                       Q(transaction__payer=request.user)
                       ).\
                       exclude(veresedakistatus__status__gt=30).\
                       exclude(veresedakistatus__status__lt=30)

        return PendingListView(query)

class LocationHandler(BaseHandler):
    """
    Location handler return vanue name for given lang/lon
    """
    allowed_methods = ('GET',)

    def read(self, request):
        try:
            lat = request.GET['lat']
            lon = request.GET['lon']

        except KeyError:
            raise PistonBadRequestException("Lat / Lon parameters not provided")

        URL = "http://api.infochimps.com/geo/location/foursquare/places/search?" +\
              "g.radius=10&g.latitude=%s&g.longitude=%s"+\
              "&apikey=verese-18HGJZXnTEkWvZQOmQVuZYvh169"

        URL = URL % (lat, lon)

        try:
            result = json.loads(urllib.urlopen(URL).read())

        except ValueError:
            return rc.THROTTLED

        return result
