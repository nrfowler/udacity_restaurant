from flask import Flask
from flask import render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from database_setup import Base, Restaurant, MenuItem
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

@app.route('/')
def HelloWorld():
    session = DBSession()
    results = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants = results)
@app.route('/rest/<int:restaurant_id>')
def RestaurantMenu():
    session = DBSession()
    rest = session.query(Restaurant).filter_by(name = "B-Bop's").one()
    return render_template('menu.html', restaurant = rest)
@app.route('/newrest')
def NewRestaurant():
    session = DBSession()
    return render_template('newrestaurant.html')
if __name__ == '__main__':
    app.debug = True
    session = DBSession()
    session.query(Restaurant).delete()
    session.query(MenuItem).delete()
    rest = Restaurant(name = "B-Bop's", city = "Des Moines")
    session.add(rest)
    rest = Restaurant(name = "McDonald's", city = "Des Moines")
    session.add(rest)
    rest = Restaurant(name = "Mars Cafe", city = "Des Moines")
    session.add(rest)
    session.commit()
    session = DBSession()
    rest = session.query(Restaurant).filter_by(name = "B-Bop's").one()
    item = MenuItem (name = "Burger", description = "A juicy burger", price = "3.60", course = "main", restaurant_id =  rest.id)
    session.add(item)
    item = MenuItem (name = "Cheese Burger", description = "A juicy cheese burger", price = "3.90", course = "main", restaurant_id =  rest.id)
    session.add(item)
    item = MenuItem (name = "Dbl. Burger", description = "A juicy double burger", price = "4.60", course = "main", restaurant_id =  rest.id)
    session.add(item)
    rest = session.query(Restaurant).filter_by(name = "Mars Cafe").one()
    item = MenuItem (name = "Coffee", description = "A up o' joe", price = "3.60", course = "main", restaurant_id =  rest.id)
    session.add(item)
    item = MenuItem (name = "Tea", description = "A cup of tea", price = "3.90", course = "main", restaurant_id =  rest.id)
    session.add(item)
    item = MenuItem (name = "Latte", description = "A tasty latte", price = "4.60", course = "main", restaurant_id =  rest.id)
    session.add(item)
    rest = session.query(Restaurant).filter_by(name = "McDonald's").one()
    item = MenuItem (name = "Coffee", description = "A up o' joe", price = "1.60", course = "main", restaurant_id =  rest.id)
    session.add(item)
    item = MenuItem (name = "Hamburger", description = "A plain Hamburger", price = "3.90", course = "main", restaurant_id =  rest.id)
    session.add(item)
    item = MenuItem (name = "Whopper", description = "A big ol' whopper", price = "4.60", course = "main", restaurant_id =  rest.id)
    session.add(item)
    session.commit()
    app.run(host = '0.0.0.0', port = 5000)
