from django.contrib import admin

from models import Consumer, Nonce, Token

# Attach Models to Admin
admin.site.register(Nonce)
admin.site.register(Consumer)
admin.site.register(Token)
