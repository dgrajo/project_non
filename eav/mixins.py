# eav/mixins.py

from sqlalchemy.ext.declarative import declared_attr


class PolymorphicEntity:

    @declared_attr
    def __mapper_args__(klass):
        return { 'polymorphic_identity' : klass.__name__ }

