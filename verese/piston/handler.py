import copy
import types
import warnings

from utils import rc
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.conf import settings
from django.utils.datastructures import SortedDict

typemapper = { }
handler_tracker = [ ]

class Field(object):
    def __init__(self, name, xform_obj=None, destination=None, required=True, iterable_xform_obj=False):
        self.name = name
        self.name_parts = [x for x in name.split('.') if x]
        self.required = required
        self.xform_obj = xform_obj
        self.iterable_xform_obj = iterable_xform_obj
        self.destination = destination or name
        if destination is None and '.' in name:
            raise ValueError('Cannot specify a non top-level attribute (%s) and not specify a destination name.' % name)

    def get_value(self, obj):
        value = obj
        for name in self.name_parts:
            try:
                value = getattr(value, name)
                # Might be attribute or callable
                if type(value) in (types.FunctionType, types.MethodType):
                    try:
                        value = value()
                    except TypeError:
                        if self.required:
                            raise TypeError("%s is a required field but not in %s." % name, value)
                        return None
            except AttributeError:
                try:
                    value = value[name]
                except (KeyError, TypeError):
                    if self.required:
                        raise KeyError("%s is a required field but not in %s" % (name, value))
                    return None

        if value is not None and self.xform_obj:
            if self.iterable_xform_obj:
                value = [self.xform_obj(x) for x in value]
            else:
                value = self.xform_obj(value)

        return value

class PistonViewMetaclass(type):
    """
    Metaclass that converts Field attributes to a dictionary called
    'base_fields', taking into account parent class 'base_fields' as well.
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(PistonViewMetaclass, cls).__new__
        parents = [b for b in bases if isinstance(b, PistonViewMetaclass)]
        if not parents:
            # If this isn't a subclass of PistonViewMetaclass, don't do anything special.
            return super_new(cls, name, bases, attrs)

        base_fields = SortedDict()
        for parent_cls in parents:
            for field in getattr(parent_cls, 'base_fields', []):
                # if the superclass has defined a field, don't add
                # that field from the base class since inspect.getmro
                # lists classes in order from super to base
                if field.destination not in base_fields:
                    base_fields[field.destination] = field

        for field in attrs.get('fields', []):
            if isinstance(field, basestring):
                field = Field(field)
            base_fields[field.destination] = field

        attrs['base_fields'] = base_fields.values()

        new_class = super_new(cls, name, bases, attrs)
        return new_class

class BasePistonView(object):
    def __new__(cls, data, *args, **kwargs):
        if isinstance(data, (list, tuple)):
            return [ cls.__new__(cls, x, *args, **kwargs) for x in data ]
        obj = object.__new__(cls)
        obj.__init__(data, *args, **kwargs)
        return obj

    def __init__(self, data):
        self.data = data
        self.fields = copy.deepcopy(self.base_fields)

    def render(self):
        result = {}
        for field in self.fields:
            value = field.get_value(self.data)
            # skip if field is None and not required
            if not (value is None and not field.required):
                destination = result
                keys = field.destination.split('.')
                sub_keys, key = keys[:-1], keys[-1]
                for sub_key in sub_keys:
                    try:
                        destination = destination[sub_key]
                    except KeyError:
                        destination[sub_key] = {}
                        destination = destination[sub_key]

                destination[key] = value
        return result

    def __emittable__(self):
        return self.render()

class PistonView(BasePistonView):
    __metaclass__ = PistonViewMetaclass

class HandlerMetaClass(type):
    """
    Metaclass that keeps a registry of class -> handler
    mappings.
    """
    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)

        def already_registered(model, anon):
            for k, (m, a) in typemapper.iteritems():
                if model == m and anon == a:
                    return k

        if hasattr(new_cls, 'model'):
            if already_registered(new_cls.model, new_cls.is_anonymous):
                if not getattr(settings, 'PISTON_IGNORE_DUPE_MODELS', False):
                    warnings.warn("Handler already registered for model %s, "
                        "you may experience inconsistent results." % new_cls.model.__name__)

            typemapper[new_cls] = (new_cls.model, new_cls.is_anonymous)
        else:
            typemapper[new_cls] = (None, new_cls.is_anonymous)

        if name not in ('BaseHandler', 'AnonymousBaseHandler'):
            handler_tracker.append(new_cls)

        return new_cls

class BaseHandler(object):
    """
    Basehandler that gives you CRUD for free.
    You are supposed to subclass this for specific
    functionality.

    All CRUD methods (`read`/`update`/`create`/`delete`)
    receive a request as the first argument from the
    resource. Use this for checking `request.user`, etc.
    """
    __metaclass__ = HandlerMetaClass

    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    anonymous = is_anonymous = False
    exclude = ( 'id', )
    fields =  ( )

    def flatten_dict(self, dct):
        return dict([ (str(k), dct.get(k)) for k in dct.keys() ])

    def has_model(self):
        return hasattr(self, 'model') or hasattr(self, 'queryset')

    def queryset(self, request):
        return self.model.objects.all()

    def value_from_tuple(tu, name):
        for int_, n in tu:
            if n == name:
                return int_
        return None

    def exists(self, **kwargs):
        if not self.has_model():
            raise NotImplementedError

        try:
            self.model.objects.get(**kwargs)
            return True
        except self.model.DoesNotExist:
            return False

    def read(self, request, *args, **kwargs):
        if not self.has_model():
            return rc.NOT_IMPLEMENTED

        pkfield = self.model._meta.pk.name

        if pkfield in kwargs:
            try:
                return self.queryset(request).get(pk=kwargs.get(pkfield))
            except ObjectDoesNotExist:
                return rc.NOT_FOUND
            except MultipleObjectsReturned: # should never happen, since we're using a PK
                return rc.BAD_REQUEST
        else:
            return self.queryset(request).filter(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        if not self.has_model():
            return rc.NOT_IMPLEMENTED

        attrs = self.flatten_dict(request.data)

        try:
            inst = self.queryset(request).get(**attrs)
            return rc.DUPLICATE_ENTRY
        except self.model.DoesNotExist:
            inst = self.model(**attrs)
            inst.save()
            return inst
        except self.model.MultipleObjectsReturned:
            return rc.DUPLICATE_ENTRY

    def update(self, request, *args, **kwargs):
        if not self.has_model():
            return rc.NOT_IMPLEMENTED

        pkfield = self.model._meta.pk.name

        if pkfield not in kwargs:
            # No pk was specified
            return rc.BAD_REQUEST

        try:
            inst = self.queryset(request).get(pk=kwargs.get(pkfield))
        except ObjectDoesNotExist:
            return rc.NOT_FOUND
        except MultipleObjectsReturned: # should never happen, since we're using a PK
            return rc.BAD_REQUEST

        attrs = self.flatten_dict(request.data)
        for k,v in attrs.iteritems():
            setattr( inst, k, v )

        inst.save()
        return rc.ALL_OK

    def delete(self, request, *args, **kwargs):
        if not self.has_model():
            raise NotImplementedError

        try:
            inst = self.queryset(request).get(*args, **kwargs)

            inst.delete()

            return rc.DELETED
        except self.model.MultipleObjectsReturned:
            return rc.DUPLICATE_ENTRY
        except self.model.DoesNotExist:
            return rc.NOT_HERE

class AnonymousBaseHandler(BaseHandler):
    """
    Anonymous handler.
    """
    is_anonymous = True
    allowed_methods = ('GET',)
