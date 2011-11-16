"""
Overloading piston resource to provide our own error handling methods
"""
import piston.resource
from piston.utils import rc

from exceptions import APIException

class Resource(piston.resource.Resource):
    def form_validation_response(self, e):
        resp = rc.BAD_REQUEST
        error_list = {}
        for key, value in e.form.errors.items():
            if key == '__all__':
                key = 'generic'
            error_list[key] = value

        resp._set_content(error_list)
        return resp

    def error_handler(self, e, request, meth, em_format):
        if isinstance(e, APIException):
            resp = getattr(rc, e.code)
            resp._set_content(e.error)
            return resp
        else:
            return super(Resource, self).error_handler(e, request, meth, em_format)
