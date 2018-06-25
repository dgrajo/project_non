# eav/__init__.py

import sqlalchemy as _sa
from keyword import iskeyword as _iskeyword
from inspect import isclass as _isclass
from .attr import AttributeDescriptor as Attribute
from .models import Entity, PolymorphicMixin
from .models import build_attribute_table
from .common import Base


__all__ = [
    'schema',
    'EAV',
    'Attribute',
    'Base'
    ]


def schema(schemaname, **kwargs):
    """Factory for creating an EAV schema
    with its name and attributes.
    """


    # Schema name and field name validation.
    for name in [schemaname] + list(kwargs.keys()):
        if type(name) is not str:
            raise TypeError('Schema name and field names must be strings')
        if not name.isidentifier():
            raise ValueError('Schema name and field names must be valid '
                    f'identifier: {name!r}'
                    )
        if _iskeyword(name):
            raise ValueError('Schema name and field names cannot be a '
                    f'keyword: {name!r}'
                    )

    seen = set()

    for name in kwargs.keys():
        if name in seen:
            raise ValueError(f'Duplicate field name: {name!r}')

        seen.add(name)

    # Validate field value data type.
    for data_type in set(kwargs.values()):
        if _isclass(data_type):
            if not issubclass(data_type, _sa.sql.type_api.TypeEngine):
                raise TypeError(
                    f'{data_type!r} is not a valid sqlalchemy data type'
                    )
        elif not isinstance(data_type, _sa.sql.type_api.TypeEngine):
            raise TypeError(f'{data_type!r} is not a valid sqlalchemy data type')

    # Constructor
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    __init__.__doc__ = f'Create new EAV instances of {schemaname} schema.'
    __init__.__qualname__ = f'{schemaname}.{__init__.__name__}'

    # Construct namespace
    namespace = {
        '__doc__' : f'{schemaname}({list(kwargs.keys())})',
        '__slots__' : [],
        '__init__' : __init__,
        }

    # Add attributes to namespace
    for name, data_type in kwargs.items():
        namespace[name] = Attribute(data_type)

    # Create class for eav schema.
    schema = type(schemaname, (PolymorphicMixin, Entity, object), namespace)

    return schema


class EAV(PolymorphicMixin, Entity):
    """Base class for creating EAV schema
    defining attributes with Attribute descriptor.
    """
    pass
