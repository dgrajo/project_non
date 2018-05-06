import sqlalchemy

from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session, backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection



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
                    cascade="all, delete-orphan",
                    ),
                )

    attribute = relationship(
                'Attribute',
                backref='value',
                )


    def __init__(self, value, attribute=None, instance=None):
        self.instance = instance
        self.attribute = attribute
        self.value = value

    def __repr__(self):
        return "<{clsname}({value!r})>"\
                .format(
                clsname=self.__class__.__name__,
                value=self.value,
                )


class Instance(Base):

    __tablename__ = 'instance'

    id = Column(Integer, primary_key=True)

    type = Column(String(64), nullable=False)

    attributes = association_proxy(
                    'instance_attributes',
                    'attribute',
                    )

    __mapper_args__ = {
        'polymorphic_identity' : 'instance',
        'polymorphic_on' : type,
    }


    def __repr__(self):
        return"<{clsname}(id={id!r})>"\
                .format(
                    clsname=self.type,
                    id=self.id,
                    )


class Attribute(Base):

    __tablename__ = 'attribute'

    id = Column(Integer, primary_key=True, autoincrement=True)

    key = Column(String(64), nullable=False)

    entity_type = Column(String(64))

    def __init__(self, key):
        self.key = key

    def __repr__(self):
        return "{clsname}(key={key!r})"\
                .format(
                    clsname=self.__class__.__name__,
                    key=self.key,
                    )



engine = create_engine('sqlite:///:memory:', echo=True)
sess = Session(bind=engine)
MetaData.create_all(engine)
