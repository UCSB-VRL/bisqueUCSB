# Any model classes here
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import mapper, relationship
#from sqlalchemy.orm import relation, backref
from bq.core.model import DeclarativeBase, metadata, DBSession

#class SampleModel(DeclarativeBase):
#    __tablename__ = 'sample_model'
#    id = Column(Integer, primary_key=True)
#    data = Column(Unicode(255), nullable=False)
