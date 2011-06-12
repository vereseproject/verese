from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Relation(models.Model):
    user1 = models.ForeignKey(User)
    user2 = models.ForeignKey(User)
    balance = models.DecimalField(decimal_places=2)
    user1_trust_limit = models.DecimalField(decimal_places=2)
    user2_trust_limit = models.DecimalField(decimal_places=2)

class GroupVeresedaki(models.Model):
    payer = models.ForeignKey(User)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    currency = models.ForeignKey(Currency)
    #geolocation

class Veresedaki(models.Model):
    ower = models.ForeignKey(User)
    amount = models.DecimalField(decimal_places=2)
    comment = models.TextField()
    status = models.IntegerField(choices = ((1, 'Waiting'),
                                            (2, 'Verified'),
                                            (3, 'Denied'),
                                            (4, 'Canceled'))
                                 )
    group = models.ForeignKey(GroupVeresedaki)

class Currency(models.Model):
    name = models.CharField(max_length=100)
    updated = models.DateTimeField(auto_now=True)
    rate = models.DecimalField(decimal_places=4)

