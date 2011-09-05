import sys, inspect

from django.http import (HttpResponse, Http404, HttpResponseNotAllowed,
    HttpResponseForbidden, HttpResponseServerError)
from django.views.debug import ExceptionReporter
from django.views.decorators.vary import vary_on_headers
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.db.models.query import QuerySet
from django.http import Http404

from emitters import Emitter
from handler import typemapper, BaseHandler
from doc import HandlerMethod
from authentication import NoAuthentication
from utils import coerce_put_post, FormValidationError, HttpStatusCode
from utils import rc, format_error, translate_mime, MimerDataException

CHALLENGE = object()

class PistonException(Exception):
    def __init__(self, status_code, message, headers=None):
        self.status_code = status_code
        self.message = message
        self.headers = headers and headers or {}

    def __unicode__(self):
        return self.message

class PistonBadRequestException(PistonException):
    status_code = 400
    message = 'Malformed or syntactically incorrect request'

    def __init__(self, message=None, headers=None):
        message = message or self.message
        super(PistonBadRequestException, self).__init__(self.status_code, message, headers)

class PistonUnauthorizedException(PistonException):
    status_code = 401
    message = 'Request requires authentication'

    def __init__(self, message=None, headers=None):
        message = message or self.message
        super(PistonUnauthorizedException, self).__init__(self.status_code, message, headers)

class PistonForbiddenException(PistonException):
    status_code = 403
    message = 'Request of specified resource is forbidden'

    def __init__(self, message=None, headers=None):
        message = message or self.message
        super(PistonForbiddenException, self).__init__(self.status_code, message, headers)

class PistonNotFoundException(PistonException):
    status_code = 404
    message = 'Requested resource could not be located'
    def __init__(self, message=None, headers=None):
        message = message or self.message
        super(PistonNotFoundException, self).__init__(self.status_code, message, headers)

class PistonMethodException(PistonException):
    status_code = 405
    message = 'Method not allowed on requested resource'
    def __init__(self, message=None, headers=None):
        message = message or self.message
        super(PistonMethodException, self).__init__(self.status_code, message, headers)

class Response(object):
    def __init__(self):
        self.status_code = 200
        self.error_code = None
        self.error_message = ''
        self.form_errors = {}
        self.data = None
        self.headers = {}

    def transform_data(self):
        if self.error_message:
            return self.error_message
        else:
            return self.data

class EnhancedResponse(Response):
    def transform_data(self):
        return {
                'status_code': self.status_code,
                'error_code': self.error_code,
                'error_message': self.error_message,
                'form_errors': self.form_errors,
                'data': self.data,
                }

class Resource(object):
    """
    Resource. Create one for your URL mappings, just
    like you would with Django. Takes one argument,
    the handler. The second argument is optional, and
    is an authentication handler. If not specified,
    `NoAuthentication` will be used by default.
    """
    callmap = { 'GET': 'read', 'POST': 'create',
                'PUT': 'update', 'DELETE': 'delete' }

    def __init__(self, handler, authentication=None, response_class=None):
        if not callable(handler):
            raise AttributeError, "Handler not callable."

        self.response_class = response_class is not None and response_class or Response
        self.handler = handler()
        self.csrf_exempt = getattr(self.handler, 'csrf_exempt', True)

        if not authentication:
            self.authentication = (NoAuthentication(),)
        elif isinstance(authentication, (list, tuple)):
            self.authentication = authentication
        else:
            self.authentication = (authentication,)

        # Erroring
        self.email_errors = getattr(settings, 'PISTON_EMAIL_ERRORS', True)
        self.display_errors = getattr(settings, 'PISTON_DISPLAY_ERRORS', True)
        self.display_traceback = getattr(settings, 'PISTON_DISPLAY_TRACEBACK', False)
        self.stream = getattr(settings, 'PISTON_STREAM_OUTPUT', False)

    def determine_emitter(self, request, *args, **kwargs):
        """
        Function for determening which emitter to use
        for output. It lives here so you can easily subclass
        `Resource` in order to change how emission is detected.

        You could also check for the `Accept` HTTP header here,
        since that pretty much makes sense. Refer to `Mimer` for
        that as well.
        """
        em = kwargs.pop('emitter_format', None)

        if not em:
            em = request.GET.get('format', 'json')

        return em


    @property
    def anonymous(self):
        """
        Gets the anonymous handler. Also tries to grab a class
        if the `anonymous` value is a string, so that we can define
        anonymous handlers that aren't defined yet (like, when
        you're subclassing your basehandler into an anonymous one.)
        """
        if hasattr(self.handler, 'anonymous'):
            anon = self.handler.anonymous

            if callable(anon):
                return anon

            for klass in typemapper.keys():
                if anon == klass.__name__:
                    return klass

        return None

    def authenticate(self, request, rm):
        actor, anonymous = False, True

        for authenticator in self.authentication:
            if not authenticator.is_authenticated(request):
                if self.anonymous and \
                    rm in self.anonymous.allowed_methods:

                    actor, anonymous = self.anonymous(), True
                else:
                    actor, anonymous = authenticator.challenge, CHALLENGE
            else:
                return self.handler, self.handler.is_anonymous

        return actor, anonymous


    @vary_on_headers('Authorization')
    def __call__(self, request, *args, **kwargs):
        # Support emitter both through (?P<emitter_format>) and ?format=emitter.
        em_format = self.determine_emitter(request, *args, **kwargs)
        kwargs.pop('emitter_format', None)

        response = self.response_class()

        try:
            emitter, ct = Emitter.get(em_format)
        except ValueError:
            raise PistonBadRequestException("Invalid output format specified '%s'." % em_format)

        if not response.error_message:
            meth = None
            try:
                handler, meth, fields, anonymous = self.process_request(request, response, *args, **kwargs)
            except Exception, e:
                handler, meth, fields, anonymous = None, None, (), False
                self.error_handler(response, e, request, meth)

        # If we're looking at a response object which contains non-string
        # content, then assume we should use the emitter to format that
        # content
        if isinstance(response.data, HttpResponse) and not response.data._is_string:
            # TODO: fix this
            response.status_code = response.data.status_code
            # Note: We can't use result.content here because that method attempts
            # to convert the content into a string which we don't want.
            # when _is_string is False _container is the raw data
            response.data = response.data._container

        data = response.transform_data()
        srl = emitter(data, typemapper, handler, fields, anonymous)

        status_code = response.status_code
        if srl.ALWAYS_200_OK:
            status_code = 200

        try:
            """
            Decide whether or not we want a generator here,
            or we just want to buffer up the entire result
            before sending it to the client. Won't matter for
            smaller datasets, but larger will have an impact.
            """
            if self.stream: stream = srl.stream_render(request)
            else: stream = srl.render(request)

            if not isinstance(stream, HttpResponse):
                resp = HttpResponse(stream, mimetype=ct, status=status_code)
            else:
                resp = stream

            resp.streaming = self.stream

            return resp
        except HttpStatusCode, e:
            return e.response

    def process_request(self, request, response, *args, **kwargs):
        """
        NB: Sends a `Vary` header so we don't cache requests
        that are different (OAuth stuff in `Authorization` header.)
        """
        rm = request.method.upper()

        # Django's internal mechanism doesn't pick up
        # on non POST request, so we trick it a little here.
        if rm in ("PUT", "DELETE",):
            coerce_put_post(request)

        actor, anonymous = self.authenticate(request, rm)

        result = None
        if anonymous is CHALLENGE:
            class ErrorHandler(BaseHandler):
                def error(self, *args, **kwargs):
                    pass

            for func in self.callmap.values():
                setattr(ErrorHandler, func, ErrorHandler.error)

            handler = ErrorHandler()
            meth = handler.error
            fields = ()
            response.data = actor(request)
        else:
            handler = actor
            meth = None
            fields = ()

        if not response.data:
            # Translate nested datastructs into `request.data` here.
            if rm in ('POST', 'PUT', 'DELETE',):
                try:
                    translate_mime(request)
                except MimerDataException:
                    raise PistonBadRequestException('Error deserializing request data.')
                if not hasattr(request, 'data'):
                    if rm == 'POST':
                        request.data = request.POST
                    elif rm == 'PUT':
                        request.data = request.PUT
                    elif rm == 'DELETE':
                        request.data = request.DELETE

                if not request.data:
                    # In the case where no data is provided, default to an empty
                    # dictionary. Many serializers do not deal with empty string data
                    # for deserialization.
                    setattr(request, rm, {})
                    request.data = {}

            if not rm in handler.allowed_methods:
                raise PistonMethodException(headers={'Allow': handler.allowed_methods})

            meth = getattr(handler, self.callmap.get(rm, ''), None)
            if not meth:
                raise PistonNotFoundException

            # Clean up the request object a bit, since we might
            # very well have `oauth_`-headers in there, and we
            # don't want to pass these along to the handler.
            request = self.cleanup_request(request)

            response.data = meth(request, *args, **kwargs)

            fields = handler.fields

            if hasattr(handler, 'list_fields') and isinstance(response.data, (list, tuple, QuerySet)):
                fields = handler.list_fields

        return handler, meth, fields, anonymous

    @staticmethod
    def cleanup_request(request):
        """
        Removes `oauth_` keys from various dicts on the
        request object, and returns the sanitized version.
        """
        for method_type in ('GET', 'PUT', 'POST', 'DELETE'):
            block = getattr(request, method_type, { })

            if True in [ k.startswith("oauth_") for k in block.keys() ]:
                sanitized = block.copy()

                for k in sanitized.keys():
                    if k.startswith("oauth_"):
                        sanitized.pop(k)

                setattr(request, method_type, sanitized)

        return request

    # --

    def email_exception(self, reporter):
        subject = "Piston crash report"
        html = reporter.get_traceback_html()

        message = EmailMessage(settings.EMAIL_SUBJECT_PREFIX + subject,
                                html, settings.SERVER_EMAIL,
                                [ admin[1] for admin in settings.ADMINS ])

        message.content_subtype = 'html'
        message.send(fail_silently=True)


    def error_handler(self, response, e, request, meth):
        """
        Override this method to add handling of errors customized for your
        needs
        """
        response.status_code = 500
        if isinstance(e, (PistonException, PistonBadRequestException, PistonForbiddenException, PistonMethodException, PistonNotFoundException, PistonUnauthorizedException)):
            response.status_code = e.status_code
            response.error_message = e.message
            response.headers.update(e.headers)
        elif isinstance(e, FormValidationError):
            response.status_code = 400
            response.form_errors = e.form.errors
        elif isinstance(e, TypeError) and meth:
            hm = HandlerMethod(meth)
            sig = hm.signature

            msg = 'Method signature does not match.\n\n'

            if sig:
                msg += 'Signature should be: %s' % sig
            else:
                msg += 'Resource does not expect any parameters.'

            if self.display_errors:
                msg += '\n\nException was: %s' % str(e)

            response.error_message = format_error(msg)
        # TODO: As we start using Piston exceptions, the following 2 errors can be phased out
        elif isinstance(e, Http404):
            response.status_code = 404
            response.error_message = 'Not Found'
        elif isinstance(e, HttpStatusCode):
            response.error_message = e.response
        else:
            """
            On errors (like code errors), we'd like to be able to
            give crash reports to both admins and also the calling
            user. There's two setting parameters for this:

            Parameters::
             - `PISTON_EMAIL_ERRORS`: Will send a Django formatted
               error email to people in `settings.ADMINS`.
             - `PISTON_DISPLAY_ERRORS`: Will return a simple message/full traceback
               depending on `PISTON_DISPLAY_TRACEBACK`. Default is simple message
               to the caller, so he can tell you what error they got.

            If `PISTON_DISPLAY_ERRORS` is not enabled, the caller will
            receive a basic "500 Internal Server Error" message.
            """
            exc_type, exc_value, tb = sys.exc_info()
            rep = ExceptionReporter(request, exc_type, exc_value, tb.tb_next)
            if self.email_errors:
                self.email_exception(rep)
            if self.display_errors:
                if self.display_traceback:
                    response.error_message = format_error('\n'.join(rep.format_exception()))
                else:
                    response.error_message = str(e)
            else:
                raise
