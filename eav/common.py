# eav/common.py


from sqlalchemy.ext.declarative import declarative_base

__all__ = [
    'Base',
    ]

Base = declarative_base()

ACTIVE_VALUE_TABLES = dict()
