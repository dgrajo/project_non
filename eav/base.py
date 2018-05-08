# eav/base.py

from .tables import Instance, Attribute
from .mixins import PolymorphicEntity


class EAV(PolymorphicEntity, Instance):
    """
    Subclass this to access the interface for EAV ORM
    """
    pass


class AttributeDescriptor:

    def __set_name__(self, instance, name):
        self.name = name
        self.attr = Attribute(name, instance.__class__.__name__)

    def __get__(self, instance, klass):
        pass

    def __set__(self, instance, value):
        pass

    def __delete__(self, name):
        raise AttributeError('Prohibited action')
