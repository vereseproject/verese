from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from models import Relation, Transaction, Veresedaki, Currency,\
     UserProfile, VeresedakiStatus

# register the models for the admin

class VeresedakiStatusAdmin(admin.ModelAdmin):
    models = VeresedakiStatus
    list_display = ("id", "user", "veresedaki", "status")

admin.site.register(VeresedakiStatus, VeresedakiStatusAdmin)

class VeresedakiInline(admin.TabularInline):
    model = Veresedaki

class TransactionAdmin(admin.ModelAdmin):
    inlines = [VeresedakiInline]
    list_display = ("id", "payer", "total_amount",
                    "currency", "status", "created"
                    )
    ordering = ("-created",)
    search_fields = ("payer__username", "payer__last_name")
    save_on_top = True

admin.site.register(Transaction, TransactionAdmin)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = 'user'

class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ("username", "email", "first_name", "last_name",
                    "currency", "is_active")

    def currency(self, obj):
        profile = obj.get_profile()
        return profile.currency
    currency.short_description = "currency"

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)

class RelationAdmin(admin.ModelAdmin):
    list_display = ("user1", "user2", "currency", "balance")
    list_display_links = ("user1", "user2")
    search_fields = ("user1__username",)

admin.site.register(Relation, RelationAdmin)


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "symbol", "updated", "rate")
    search_fields = ("name", "code")

admin.site.register(Currency, CurrencyAdmin)
