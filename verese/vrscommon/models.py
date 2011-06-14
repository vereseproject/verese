from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum

from taggit.managers import TaggableManager

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
        return self.veresedaki_set.aggregate(Sum('amount'))['amount__sum']

    @property
    def veresedakia(self):
        return self.veresedaki_set.all()

    def __unicode__(self):
        # total amount can be cached
        return "[%s:%s]" % (self.payer, self.total_amount)

class Veresedaki(models.Model):
    ower = models.ForeignKey(User)
    amount = models.DecimalField(max_digits=7, decimal_places=2,
                                 validators=[MinValueValidator(0.01)],
                                 blank=True)
    comment = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices = ((1, 'Waiting'),
                                            (2, 'Verified'),
                                            (3, 'Denied'),
                                            (4, 'Canceled')),
                                 default = 1,
                                 blank=True,
                                 )
    group = models.ForeignKey(GroupVeresedaki)

    def save(self, *args, **kwargs):
        super(Veresedaki, self).save(args, kwargs)
        relation, created = Relation.get_or_create(user1=self.group.payer,
                                                   user2=self.ower)
        relation.balance += self.amount
        if created:
            # set currency
            relation.currency = group.currency
        relation.save(args, kwargs)

    def __unicode__(self):
        return "[%s owes %s: %s]" % (self.ower, self.group.payer, self.amount)

class Currency(models.Model):
    name = models.CharField(max_length=100)
    updated = models.DateTimeField(auto_now=True)
    rate = models.DecimalField(max_digits=8, decimal_places=4,
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

def user_post_save(sender, instance, **kwargs):
    """Create the user profile when the user is created."""
    profile, created = UserProfile.objects.get_or_create(user=instance)
    if created:
        profile.save()

models.signals.post_save.connect(user_post_save, sender=User)
