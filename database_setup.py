import sys
from sqlalchemy import
Column, ForeignKey, Integer, string

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

##eof##

class Shelter(Base):
    __tablename__ = 'shelter'
    name = Column(String(80), nullable = False)
    city = Column(String(80), nullable = False)
    state = Column(String(80), nullable = False)
    zipCode = Column(String(80), nullable = False)
    website = Column(String(80), nullable = False)
    address = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)

class Puppy(Base):
    __tablename__ = 'puppy'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    gender = Column(String(1), nullable = False)
    weight = Column(Float, nullable = False)
    picture = Column(String(80), nullable = False)
    date_of_birth = Column(Date, nullable = False)
    shelter_id = Column(Integer, ForeignKey('shelter.id'))


    engine = create_engine( 'sqlite:///restaurantmenu.db')
    Base.metadata.create_all(engine)
