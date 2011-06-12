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
                                  validators=[MinValueValidator(0.01)])
    user1_trust_limit = models.DecimalField(max_digits=5, decimal_places=2,
                                            validators=[MinValueValidator(0)])
    user2_trust_limit = models.DecimalField(max_digits=5, decimal_places=2,
                                            validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ( ('user1', 'user2') )

    def save(self):
        # user1 is always the user with the smallest user.id
        if user1.id > user2.id:
            tmp = user1
            user1 = user2
            user2 = tmp

        return super(Relation, self).save()

class GroupVeresedaki(models.Model):
    payer = models.ForeignKey(User)
    comment = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    currency = models.ForeignKey("Currency")
    tags = TaggableManager(blank=True)
    #geolocation

    class Meta:
        verbose_name_plural = "Group Veresedakia"

    @property
    def total_amount(self):
        return self.veresedaki_set.aggregate(Sum('amount'))['amount__sum']

    def __unicode__(self):
        # total amount can be cached
        return "[%s:%s]" % (self.payer, self.total_amount)

class Veresedaki(models.Model):
    ower = models.ForeignKey(User)
    amount = models.DecimalField(max_digits=7, decimal_places=2,
                                 validators=[MinValueValidator(0.01)])
    comment = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices = ((1, 'Waiting'),
                                            (2, 'Verified'),
                                            (3, 'Denied'),
                                            (4, 'Canceled')),
                                 default = 1
                                 )
    group = models.ForeignKey(GroupVeresedaki)

    def clean(self):
        if self.ower == self.group.payer:
            raise ValidationError("Ower cannot be the same person as payer")

        return self.ower

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

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    pin = models.IntegerField(null=True, blank=True)
    currency = models.ForeignKey(Currency)

# def create_user_profile(sender, instance, **kwargs):
#     profile, created = UserProfile.objects.get_or_create(user=instance)

# post_save.connect(create_user_profile, sender=User)


def create_userprofile(sender, **kw):
    user = kw["instance"]
    if kw["created"]:
        profile = UserProfile(user=user)
        profile.save()

post_save.connect(create_userprofile, sender=User, dispatch_uid="users-profilecreation-signal")
