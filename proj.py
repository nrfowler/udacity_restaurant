from flask import Flask, request, redirect, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from database_setup import Base, Restaurant, MenuItem
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
from flask import flash
import requests
import random, string

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

    # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
	del login_session['access_token']
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	del login_session['picture']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    else:

    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

@app.route('/', methods=['GET'])
def HelloWorld():
    session = DBSession()
    results = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants = results, username = login_session['username'])
@app.route('/restaurant', methods=['GET'])
def RestaurantShow():
    session = DBSession()
    results = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants = results, username = login_session['username'])
@app.route('/login',methods=['GET'])
def Login():
    return render_template('login.html')
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
