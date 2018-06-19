# eav/common.py


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy import event


__all__ = [
    'Base',
    'set_sqlite_pragma'
    ]


Base = declarative_base()

ACTIVE_VALUE_TABLES = dict()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
