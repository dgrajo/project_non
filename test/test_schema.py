# test/test_schema.py

from eav import schema, Base
from sqlalchemy import create_engine
from sqlalchemy import Integer, String
from sqlalchemy.orm import Session
import pytest


class TestSchema:


    def setup_class(class_):
        class_.engine = create_engine('sqlite:///:memory:')

    def teardown_class(class_):
        pass

    def teardown_method(self, method):
        if len(self.s.new) > 0 or len(self.s.dirty) > 0:
            self.s.commit()

    def setup_method(self, method):
        self.s = Session(self.engine)
        self.Employee = schema(
            'Employee',
            firstname=String(16),
            lastname=String(16),
            age=Integer(),
            )
        Base.metadata.create_all(self.__class__.engine)

    def test_number_0_1(self):
        Employee = self.Employee
        emp = Employee(
                firstname='Chrstian',
                lastname='Grajo',
                age=29,
                )
        self.s.add(emp)
        self.s.commit()

        emp_db = self.s.query(Employee).filter(Employee.id == 1).one()

        assert emp.firstname == emp_db.firstname and emp.lastname == emp_db.lastname
