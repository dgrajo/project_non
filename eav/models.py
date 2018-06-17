# eav/model.py

import sqlalchemy
from inspect import isclass as _isclass
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declared_attr
from .common import Base, ACTIVE_VALUE_TABLES


__all__ = [
    'Entity',
    'Attribute',
    ]


class PolymorphicMixin(object):

    @declared_attr
    def __mapper_args__(class_):
        return {
            'polymorphic_identity' : class_.__qualname__,
            }


class AttributeMixin(object):

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)

    @declared_attr
    def entity_id(class_):
        return Column(Integer, ForeignKey('entity.id'))

    @declared_attr
    def __table_args__(class_):
        return (
            UniqueConstraint('name', 'entity_id'),
            )

    def __repr__(self):
        return "{classname}({value!r})"\
            .format(
                classname=self.__class__.__qualname__,
                value=self.value,
                )


class Entity(Base):

    __tablename__ = "entity"

    id = Column(Integer, primary_key=True)
    schema = Column(String(32), nullable=False)

    __mapper_args__ = {
        'polymorphic_on' : schema,
        'polymorphic_identity' : 'Entity',
        }

    def __repr__(self):
        return f'{self.__class__.__qualname__}({self.id!r})'


def table_class_name(data_type):

    if _isclass(data_type):
        tablename = f'{data_type.__qualname__}'
    else:
        classname = data_type.__class__.__qualname__
        if hasattr(data_type, 'name'):
            tablename = f'{classname}_{data_type.name}'
        elif hasattr(data_type, 'length'):
            tablename = f'{classname}_{data_type.length}'
        else:
            tablename = f'{classname}'

    return tablename


def build_attribute_table(data_type):
    """Factory function for creating an attribute table
    for a specific sqlalchemy data type.
    """

    entity_class = Entity
    cache = ACTIVE_VALUE_TABLES

    # Validate if the provided data type is supported by sqlalchemy
    # raise TypeError if not.
    if _isclass(data_type):
        if not issubclass(data_type, sqlalchemy.sql.type_api.TypeEngine):
            raise TypeError(f'{data_type} is not a valid sqlalchemy data type')

    if not isinstance(data_type, sqlalchemy.sql.type_api.TypeEngine):
        raise TypeError(f'{data_type} is not a valid sqlalchemy data type')

    classname = table_class_name(data_type)

    # Return the value table for the data type if already built
    if classname in cache:
        return cache[classname]

    namespace = {
        '__tablename__' : classname.lower(),
        'value' : sqlalchemy.Column(data_type, nullable=False),
        }

    table = type(classname, (AttributeMixin, Base), namespace)

    setattr(
        entity_class,
        f'_rel_{classname.lower()}',
        relationship(classname,
            backref=f'_ref_{classname.lower()}',
            collection_class=attribute_mapped_collection('name'),
            )
        )

    # Store the built table in a cache.
    cache[classname] = table

    return table


class EntityAttributeDescriptor(object):
    """Accessor descriptor to the collection of mapped attribute
    in the Entity class
    """

    __slots__ = ['table', 'python_type', 'rel', 'name']

    def __init__(self, data_type):
        self.table = build_attribute_table(data_type)
        self.python_type = self.table.value.type.python_type
        self.rel = f'_rel_{self.table.__tablename__}'

    def __set_name__(self, class_, name):
        self.name = name

    def __get__(self, object_, class_):
        try:
            attrs = getattr(object_, self.rel)
            return attrs[self.name].value
        except KeyError as e:
            return None

    def __set__(self, object_, value):
        if not isinstance(value, self.python_type):
            raise TypeError(f'{self.name} must be of type {self.python_type}')
        try:
            attrs = getattr(object_, self.rel)
            attr = attrs[self.name]
        except KeyError as e:
            if value is not None:
                attrs[self.name] = self.table(name=self.name, value=value)
        else:
            if value is not None:
                attr.value = value
            else:
                del(attrs[self.name])

    def __delete__(self, object_):
        raise AttributeError(
                f'`del()` action not allowed on attribute {self.name}'
                )


