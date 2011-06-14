from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from models import Relation, GroupVeresedaki, Veresedaki, Currency, UserProfile

# register the models for the admin
admin.site.register(Currency)

class VeresedakiInline(admin.TabularInline):
    model = Veresedaki

class GroupVeresadakiAdmin(admin.ModelAdmin):
    inlines = [VeresedakiInline]
    list_display = ("payer", "total_amount", "created")
    ordering = ("-created",)
    search_fields = ("payer__username", "payer__last_name")
    save_on_top = True

admin.site.register(GroupVeresedaki, GroupVeresadakiAdmin)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = 'user'

class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)

class RelationAdmin(admin.ModelAdmin):
    list_display = ("user1", "user2", "balance")
    list_display_links = ("user1", "user2")
    search_fields = ("user1__username",)

admin.site.register(Relation, RelationAdmin)
