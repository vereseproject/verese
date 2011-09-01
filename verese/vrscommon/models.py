from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum, Q

from taggit.managers import TaggableManager

status_choices = ((40, 'Verified'),
                  (30, 'Waiting'),
                  (20, 'Denied'),
                  (10, 'Canceled')
                  )

# Create your models here.
class Relation(models.Model):
    user1 = models.ForeignKey(User, related_name="user1")
    user2 = models.ForeignKey(User, related_name="user2")
    balance = models.DecimalField(max_digits=7, decimal_places=2,
                                  default=0)
    user1_trust_limit = models.DecimalField(max_digits=5, decimal_places=2,
                                            validators=[MinValueValidator(0)],
                                            default=0,
                                            blank=True)
    user2_trust_limit = models.DecimalField(max_digits=5, decimal_places=2,
                                            validators=[MinValueValidator(0)],
                                            default=0,
                                            blank=True)
    currency = models.ForeignKey("Currency")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ( ('user1', 'user2') )

    def __unicode__(self):
        return "%s %d %s" % (self.user1, self.balance, self.user2)

    def clean(self):
        if self.user1 == self.user2:
            raise ValidationError("User1 cannot be the same as User2")

        return super(Relation, self).clean()

    def save(self, *args, **kwargs):
        # user1 is always the user with the smallest user.id
        if self.user1.id > self.user2.id:
            tmp = user1
            self.user1 = self.user2
            self.user2 = tmp

        return super(Relation, self).save(*args, **kwargs)

    @classmethod
    def get_or_create(self, user1, user2, **kwargs):
        # we user our own get_or_create, instead of
        # self.objects.get_or_create to solve user1, user2 position
        # problem
        if user1.id > user2.id:
            return self.objects.get_or_create(user1=user2,
                                              user2=user1, **kwargs)
        else:
            return self.objects.get_or_create(user1=user1,
                                              user2=user2, **kwargs)

class GroupVeresedaki(models.Model):
    payer = models.ForeignKey(User)
    comment = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    currency = models.ForeignKey("Currency")
    tags = TaggableManager(blank=True)
    # geolocation

    class Meta:
        verbose_name_plural = "Group Veresedakia"

    @property
    def total_amount(self):
        return self.veresedakia.aggregate(amount=Sum('amount'))['amount']

    @property
    def status(self):
        """
        Return the status of GroupVeresedaki based on the status of Veresedakia.

        The lowest value of Veresedakia is returned as status.

        e.g.
        If you have 3 Veresedakia with the following status values
        (30, Waiting), (40, Verified) and (20, Denied)

        the status of GroupVeresedaki will be (20, Denied)
        """
        print self.veresedakia.values_list('status__status', flat=True)
        status_value = min(self.veresedakia.values_list('status__status', flat=True) or [1])
        for status in status_choices:
            if status[0] == status_value:
                return status[1]

    @property
    def veresedakia(self):
        """
        Shortcut to self.veresedaki_set
        """
        return self.veresedaki_set.all()

    def __unicode__(self):
        # total amount can be cached
        return "[%s:%s]" % (self.payer, self.total_amount)

class Veresedaki(models.Model):
    ower = models.ForeignKey(User)
    amount = models.DecimalField(max_digits=7, decimal_places=2,
                                 validators=[MinValueValidator(0.01)],
                                 blank=True)
    local_amount = models.DecimalField(help_text="Amount converted to relation currency",
                                       max_digits=7, decimal_places=2,
                                       validators=[MinValueValidator(0.01)],
                                       blank=True)
    comment = models.TextField(blank=True, null=True)
    status = models.ForeignKey("VeresedakiStatus", blank=True)
    group = models.ForeignKey(GroupVeresedaki)
    # currency = models.ForeignKey("Currency")

    def save(self, *args, **kwargs):
        # create or get relation
        relation, created = Relation.get_or_create(user1=self.group.payer,
                                                   user2=self.ower)
        if created:
            # set currency
            relation.currency = self.group.currency

        # calculate amount in relation currency
        self.local_amount = self.amount / self.group.currency.rate * relation.currency.rate

        # add balance
        relation.balance += self.amount
        relation.save(args, kwargs)

        # add status
        if self.status == None:
            self.status = VeresedakiStatus(user=self.group.payer, status=1)
            self.status.save()

        super(Veresedaki, self).save(args, kwargs)

    def __unicode__(self):
        return "[%s owes %s: %s]" % (self.ower, self.group.payer, self.amount)

    class Meta:
        verbose_name_plural = "veresedakia"


class VeresedakiStatus(models.Model):
    """
    Log the status changes of a Veresadaki.

    When you want to change the status of a Veresedaki you create a
    new VeresedakiStatus. Do not change already existing statuses
    """
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices = status_choices,
                                 default = 30,
                                 blank=True,
                                 )

    def __unicode__(self):
        return self.get_status_display()

    class Meta:
        verbose_name_plural = "veresedakia statuses"

class Currency(models.Model):
    """
    Currency Rate Database.
    Rates use Euro as reference
    """
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=1, null=True, blank=True)
    code = models.CharField(max_length=3, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    rate = models.DecimalField(max_digits=9, decimal_places=5,
                               validators=[MinValueValidator(0.0001)])

    class Meta:
        verbose_name_plural = "currencies"

    def __unicode__(self):
        return self.name

class UserBalance(models.Model):
    user = models.ForeignKey(User)
    currency = models.ForeignKey(Currency)
    amount = models.DecimalField(max_digits=7, decimal_places=2,
                                 validators=[MinValueValidator(0.01)])

    class Meta:
        unique_together = (("user", "currency"))

    def save(self, *args, **kwargs):
        super(UserBalance, self).save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    pin = models.IntegerField(null=True, blank=True)
    currency = models.ForeignKey(Currency)
    wants_email = models.BooleanField(default=True)

    def __unicode__(self):
        return unicode(self.user)

    @property
    def balance(self):
        """
        Calculates overall balance.

        Note that the balance is calculated in user's currency. User's
        relations that have difference base currency are converted on
        the fly. Hence balance calculation is and approximation
        """
        total_amount = 0

        # find the currencies user uses
        currencies = Relation.objects.\
                     filter(Q(user1=self.user)|Q(user2=self.user)).\
                     values_list('currency', flat=True).distinct()

        # now calculate Sums per currency and convert to local currency
        for currency_id in currencies:
            currency = Currency.objects.get(pk=currency_id)
            amount = Relation.objects.\
                     filter(Q(user1=self.user)|Q(user2=self.user)).\
                     filter(currency=currency).\
                     aggregate(balance=Sum('balance'))['balance']
            total_amount += amount / currency.rate * self.currency.rate

        return total_amount

    @property
    def balance_detailed(self):
        """
        Calculates overall balance per currency used by user
        """
        total_amounts = Relation.objects.\
                        filter(Q(user1=self.user)|Q(user2=self.user)).\
                        values('currency').\
                        annotate(balance=Sum('balance'))

        for amount in total_amounts:
            amount['currency'] = Currency.objects.get(pk=amount['currency'])

        return total_amounts


def user_post_save(sender, instance, **kwargs):
    """Create the user profile when the user is created."""
    profile, created = UserProfile.objects.get_or_create(user=instance)

models.signals.post_save.connect(user_post_save, sender=User)
