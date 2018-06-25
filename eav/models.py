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

    name = Column(String(32), primary_key=True)

    @declared_attr
    def entity_id(class_):
        return Column(
                Integer,
                ForeignKey('entity.id', ondelete='CASCADE'),
                primary_key=True,
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

    elif not isinstance(data_type, sqlalchemy.sql.type_api.TypeEngine):
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
            cascade='all, delete-orphan',
            )
        )

    # Store the built table in a cache.
    cache[classname] = table

    return table

