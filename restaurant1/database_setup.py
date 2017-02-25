import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric, Float

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

##eof##

class Restaurant(Base):
    __tablename__ = 'restaurant'
    name = Column(String(80), nullable = False)
    city = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)

class MenuItem(Base):
    __tablename__ = 'menu_item'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))


    engine = create_engine( 'sqlite:///restaurantmenu.db')
    Base.metadata.create_all(engine)
