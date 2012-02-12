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
    ctx = RequestContext(request,
                         {
                             'currencies':Currency.objects.all()
                             }
                         )

    return render_to_response('verese.html', ctx)


def add(request):
    ctx = RequestContext(request,
                         {
                             'active': 'add'
                             }
                         )

    return render_to_response('add.html', ctx)

def activity(request):
    ctx = RequestContext(request,
                         {
                             'active': 'activity'
                             }
                         )

    return render_to_response('activity.html', ctx)

def connections(request):
    ctx = RequestContext(request,
                         {
                             'active': 'connections'
                             }
                         )

    return render_to_response('connections.html', ctx)

def dashboard(request):
    ctx = RequestContext(request,
                         {
                             'active': 'dashboard'
                             }
                         )

    return render_to_response('dashboard.html', ctx)

