import re
import inspect
import types
from functools import update_wrapper


def is_interactive():
    import __main__ as main
    return not hasattr(main, '__file__')


__interactive_mode__ = is_interactive()


def     get_attr_docstring(class_type, attr_name):
    if attr_name == 'get':
        attr_name = '__call__'

    attr = getattr(class_type, attr_name, None)
    if attr and attr.__doc__:
        return re.sub(r' {3,}', '', attr.__doc__)


def default_attr_filter(x):
    return not x.startswith('_')


def get_class_docstring(class_type, attr_filter=default_attr_filter, extended=False):
    def attr_format(x):
        attr = getattr(class_type, x)

        if type(attr) == property:
            name = f'.{x}'
        else:
            if extended:
                sig = str(inspect.signature(attr)).replace('self, ', '')
            else:
                sig = '()'
            name = f'.{x}{sig}'

        if extended:
            doc = get_attr_docstring(class_type, x)
        else:
            doc = ''

        return f'{name}{doc}'

    return '\n'.join(map(attr_format, filter(attr_filter, dir(class_type))))


def inline_doc(method):
    if not __interactive_mode__:
        return method

    doc = [repr(method)]
    if method.__doc__:
        doc.append(re.sub(r' {3,}', '', method.__doc__))

    class CustomReprDescriptor:
        def __get__(self, instance, owner):
            class MethodWrapper:
                def __init__(self):
                    self.class_instance = instance
                    self.doc = '\n'.join(doc)

                def __call__(self, *args, **kwargs):
                    return method(self.class_instance, *args, **kwargs)

                def __repr__(self):
                    return self.doc

            return update_wrapper(MethodWrapper(), method)

    return CustomReprDescriptor()


class InlineDocstring(type):

    def __new__(mcs, name, bases, attrs, **kwargs):
        new_attrs = {}
        for attr_name, attr in attrs.items():
            if isinstance(attr, types.FunctionType) and attr.__doc__ and not attr_name.startswith('_'):
                attr = inline_doc(attr)
            new_attrs[attr_name] = attr
        return type.__new__(mcs, name, bases, new_attrs, **kwargs)
