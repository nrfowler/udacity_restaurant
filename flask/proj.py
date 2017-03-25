from flask import Flask, request, redirect, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from database_setup import Base, Restaurant, MenuItem
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

@app.route('/', methods=['GET'])
def HelloWorld():
    session = DBSession()
    results = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants = results)
@app.route('/rest/<int:restaurant_id>', methods=['GET'])
def RestaurantMenu(restaurant_id):
    session = DBSession()
    rest = session.query(Restaurant).filter_by(id = restaurant_id).one()
    return render_template('menu.html', restaurant = rest,
        items = session.query(MenuItem).filter_by(
            restaurant_id = restaurant_id).all())
@app.route('/newrest', methods=['GET'])
def NewRestaurant():
    if request.method =='GET':
        session = DBSession()
        return render_template('newrestaurant.html' )
@app.route('/newitem/<int:restaurant_id>', methods=['GET'])
def NewMenuItem(restaurant_id):
    if request.method =='GET':

        return render_template('newmenuitem.html' )
    else:
        session = DBSession()
        newItem = MenuItem(name = request.form['name'],
            price = request.form['price'],
            description = request.form['description'],
            course = request.form['course'], restaurant_id = restaurant_id)
        session.add(newItem)
        session.commit()
        return redirect('/rest/'+str(restaurant_id),
            restaurant = session.query(Restaurant).filter_by(
                id = restaurant_id).one(),
            items = session.query(MenuItem).filter_by(
                restaurant_id = restaurant_id).all())
@app.route('/delrest/<int:restaurant_id>', methods=['GET'])
def DeleteRestaurant(restaurant_id):
    if request.method =='GET':
        session = DBSession()
        return render_template('deleterestaurant.html',
            restaurant = session.query(Restaurant).filter_by(
                id = restaurant_id).one())
@app.route('/editrest/<int:restaurant_id>', methods=['GET'])
def EditRestaurant(restaurant_id):
    if request.method =='GET':
        session = DBSession()
        return render_template('editrestaurant.html',
             restaurant = session.query(Restaurant).filter_by(
                id = restaurant_id).one())
@app.route('/edititem/<int:id>', methods=['GET'])
def EditItem(id):
    if request.method =='GET':
        session = DBSession()
        return render_template('editmenuitem.html',
            item = session.query(Restaurant).filter_by(id = id).one())
@app.route('/delitem/<int:id>', methods=['GET'])
def DeleteItem(id):
    if request.method =='GET':
        session = DBSession()
        return render_template('deletemenuitem.html',
            item = session.query(Restaurant).filter_by(id = id).one())


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
    item = MenuItem (name = "Burger",
        description = "A juicy burger", price = "3.60",
        course = "main", restaurant_id =  rest.id)
    session.add(item)
    item = MenuItem (name = "Cheese Burger",
        description = "A juicy cheese burger", price = "3.90",
        course = "main", restaurant_id =  rest.id)
    session.add(item)
    item = MenuItem (name = "Dbl. Burger",
        description = "A juicy double burger", price = "4.60",
        course = "main", restaurant_id =  rest.id)
    session.add(item)
    rest = session.query(Restaurant).filter_by(name = "Mars Cafe").one()
    item = MenuItem (name = "Coffee", description = "A up o' joe",
        price = "3.60", course = "main", restaurant_id =  rest.id)
    session.add(item)
    item = MenuItem (name = "Tea", description = "A cup of tea",
        price = "3.90", course = "main", restaurant_id =  rest.id)
    session.add(item)
    item = MenuItem (name = "Latte", description = "A tasty latte",
        price = "4.60", course = "main", restaurant_id =  rest.id)
    session.add(item)
    rest = session.query(Restaurant).filter_by(name = "McDonald's").one()
    item = MenuItem (name = "Coffee", description = "A up o' joe",
        price = "1.60", course = "main", restaurant_id =  rest.id)
    session.add(item)
    item = MenuItem (name = "Hamburger", description = "A plain Hamburger",
        price = "3.90", course = "main", restaurant_id =  rest.id)
    session.add(item)
    item = MenuItem (name = "Whopper", description = "A big ol' whopper",
        price = "4.60", course = "main", restaurant_id =  rest.id)
    session.add(item)
    session.commit()
    app.run(host = '0.0.0.0', port = 5000)
