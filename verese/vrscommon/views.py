# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings

from vrscommon.models import Currency

def request_token_ready(request, token):
    error = request.GET.get('error', '')
    ctx = RequestContext(request, {
        'error' : error,
        'token' : token
    })
    return render_to_response(
        'piston/request_token_ready.html',
        context_instance = ctx
    )

def main(request):
    try:
        site_edition = settings.SITE_EDITION

    except:
        site_edition = 'unset'

    ctx = {
        'site_edition': site_edition,
        'currencies':Currency.objects.all()
        }

    return render_to_response('verese.html', ctx)
