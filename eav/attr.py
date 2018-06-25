# eav/attr.py

from .models import build_attribute_table


__all__ = [
    'EntityAttributeDescriptor',
    ]

class InstanceAttrMixin(object):

    def __get__(self, instance, class_):
        try:
            attrs = getattr(instance, self.rel)
            return attrs[self.name].value
        except KeyError:
            return None

    def __set__(self, instance, value):
        # Setting the value to None deletes its entry from the database
        if value is None:
            self.__delete__(instance)

        if not isinstance(value, self.python_type):
            raise ValueError(f'{value} is not type '
                    f'{self.python_type.__qualname__}')

        attrs = getattr(instance, self.rel)

        try:
            attrs[self.name].value = value
        except KeyError:
            attrs[self.name] = self.table(name=self.name, value=value)
                

    def __delete__(self, instance):
        """Deleting an attribute of an instance
        removes its entry from the database.
        """
        attrs = getattr(instance, self.rel)        
        try:
            del(attrs[self.name])
        except KeyError:
            # Do nothing if the attribute does not exist.
            pass
            

class AttributeDescriptor(InstanceAttrMixin):
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

    def __get__(self, instance, class_):
        if instance is not None:
            return super().__get__(instance, class_)
        else:
            return self.table

    def __set__(self, instance, value):
        super().__set__(instance, value)
