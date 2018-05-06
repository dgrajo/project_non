import sqlalchemy

from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session, backref
from sqlalchemy.ext.associationproxy import association_proxy


Base = declarative_base()
MetaData = Base.metadata



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
                    cascade="all, delete-orphan"
                    ),
                )

    attribute = relationship('Attribute')

    def __init__(self, value, attribute=None, instance=None):
        self.instance = instance
        self.attribute = attribute
        self.value = value


class Instance(Base):

    __tablename__ = 'instance'

    id = Column(Integer, primary_key=True)

    type = Column(String(64), nullable=False)

    name = Column(String(64), nullable=False, unique=True)

    attributes = association_proxy(
                    'instance_attributes',
                    'attribute',
                    )

    def __init__(self, name):
        self.name = name


    def __repr__(self):
        return"<{clsname}(name={name!r})>"\
                .format(
                    clsname=self.type,
                    name=self.name,
                    )


class Attribute(Base):

    __tablename__ = 'attribute'

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(64), nullable=False)

    entity_type = Column(String(64))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "{clsname}(name={name!r})"\
                .format(
                    clsname=self.__class__.__name__,
                    name=self.name,
                    )



engine = create_engine('sqlite:///:memory:', echo=True)
sess = Session(bind=engine)
MetaData.create_all(engine)
