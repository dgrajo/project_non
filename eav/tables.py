# eav/tables.py

import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship, Session, backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection



Base = declarative_base()
MetaData = Base.metadata



class Instance(Base):

    __tablename__ = 'instance'

    id = Column(Integer, primary_key=True)

    type = Column(String(32), nullable=False)

    name = Column(String(128), nullable=False)

    _proxied_attributes = association_proxy(
        'instance_attributes',
        'attribute',
        )

    __table_args__ = (
        UniqueConstraint('type', 'name'),    
        )

    __mapper_args__ = {
        'polymorphic_identity' : 'instance',
        'polymorphic_on' : type,
        }

    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return"<{clsname}({name!r})>"\
                .format(
                    clsname=self.type,
                    name=self.name,
                    )


class Attribute(Base):

    __tablename__ = 'attribute'

    id = Column(Integer, primary_key=True, autoincrement=True)

    key = Column(String(64), nullable=False)

    entity = Column(String(64))

    __table_args__ = (
        UniqueConstraint('entity', 'key'),
        )

    def __init__(self, key, entity):
        self.key = key
        self.entity = entity

    def __repr__(self):
        return "{clsname}(key={key!r})"\
                .format(
                    clsname=self.__class__.__name__,
                    key=self.key,
                    )


class ValueMixin:

    @declared_attr
    def __tablename__(klass):
        return klass.__name__.lower()

    @declared_attr
    def attribute_id(klass):
        return Column(
            Integer,
            ForeignKey('attribute.id'),
            primary_key=True,
            )

    @declared_attr
    def instance_id(klass):
        return Column(
            Integer,
            ForeignKey('instance.id'),
            primary_key=True,
            )

    @declared_attr
    def instance(klass):
        return relationship(
            'Instance'
            backref=backref(
                'instance_attribute_{name!s}'\
                    .format(name=lambda : klass.__tablename__),
                cascade="all, delete-orphan",
                )
            )

    @declared_attr
    def attribute(klass):
        return relationship('Attribute')


class Value(Base):

    __tablename__ = 'value'

    attribute_id = Column(
        Integer,
        ForeignKey('attribute.id'),
        primary_key=True,
        )

    instance_id = Column(
        Integer,
        ForeignKey('instance.id'),
        primary_key=True,
        )

    value = Column(String(128))

    instance = relationship(
        'Instance',
        backref=backref(
            'instance_attributes',
            cascade="all, delete-orphan",
            ),
        )

    attribute = relationship('Attribute')


    def __repr__(self):
        return "<{clsname}({value!r})>"\
                .format(
                    clsname=self.__class__.__name__,
                    value=self.value,
                    )





engine = create_engine('sqlite:///eav.db', echo=True)
sess = Session(bind=engine)
MetaData.create_all(engine)
