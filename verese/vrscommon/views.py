# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

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

@login_required
def main(request):
    return render_to_response('verese.html')

@login_required
def welcome(request):
    ctx = {
        'currencies':Currency.objects.all()
        }
    return render_to_response('welcome.html', ctx)
