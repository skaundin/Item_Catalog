from gauth import authorized
import requests
from flask import make_response
import string
import random
import httplib2
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
from flask_httpauth import HTTPBasicAuth
from catalog_database_setup import Base, Category, Item
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_session import Session
from flask import Flask, render_template, url_for
from flask import request, redirect, flash, jsonify
from flask import abort, json, session
# NEW IMPORTS

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)
app.secret_key = b'i\x18\xd4\x93\xe9!\x87\xb7\x88E\x84>\xc1\x01\x96\x1d'
app.debug = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config.from_object(__name__)
Session(app)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# JSON


@app.route('/catalog/JSON/')
def itemCatalogJSON():
    db_session = DBSession()
    x = db_session.query(Item).all()
    return jsonify(items=[i.serialize for i in x])


@app.route('/catalog/<category_name>/JSON/')
def categoryNameJSON(category_name):
    db_session = DBSession()
    categories = db_session.query(Category)
    category = db_session.query(Category).filter_by(name=category_name).one()
    print(category)
    items = db_session.query(Item).filter_by(category_id=category.id).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/catalog/<category_name>/items/<item_name>/JSON/')
def itemDescJSON(category_name, item_name):
    db_session = DBSession()
    category = db_session.query(Category).filter_by(name=category_name).one()
    item = db_session.query(Item).filter_by(
        category_id=category.id).filter_by(name=item_name).one()
    return jsonify(item=[i.serialize for i in item])


@app.route('/gconnect', methods=['POST'])
def gconnect():

    # If this request does not have `X-Requested-With` header, this could be
    # CSRF
    if not request.headers.get('X-Requested-With'):
        abort(403)

    # Validate state token
    if request.args.get('state') != session['state']:
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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id
    session['user_id'] = credentials.id_token['email']

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    output = ''
    output += '<h1>Welcome, '
    print("done!")
    response = make_response(output, 200)
    response.headers['Content-Type'] = 'application/html'
    return response

# home page
@app.route("/", methods=['GET'])
def home():
    session.permanent = False
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    session['state'] = state
    db_session = DBSession()
    categories = db_session.query(Category)
    return render_template('home.html', categories=categories, STATE=state)


# deleteing an item
@app.route("/catalog/<category_name>/<item_name>/delete",
           methods=['GET', 'POST'])
@authorized
def delete_item(category_name, item_name):
    db_session = DBSession()
    category = db_session.query(Category).filter_by(
        name=category_name).one()
    item_to_be_deleted = db_session.query(Item).filter_by(
        category_id=category.id).filter_by(name=item_name).one()
    if request.method == 'POST':
        if item and item.user_id != session['user_id']:
            flash("Error")
            state = session['state']
            categories = db_session.query(Category)
            return render_template('home.html',
                                   categories=categories, STATE=state)
        else:
            db_session.delete(item_to_be_deleted)
            db_session.commit()
            return catalog_desc(category_name)
    return render_template('delete.html',
                           item_name=item_to_be_deleted.name,
                           category_name=category.name)

# catalog list
@app.route("/catalog/<category_name>/items/", methods=['GET'])
def catalog_desc(category_name):
    db_session = DBSession()
    categories = db_session.query(Category)
    category = db_session.query(Category).filter_by(name=category_name).one()
    print(category)
    items = db_session.query(Item).filter_by(
        category_id=category.id).all()
    return render_template('category.html',
                           items=items,
                           category_name=category.name,
                           categories=categories)

# description of an item for a category
@app.route("/catalog/<category_name>/<item_name>/", methods=['GET', 'POST'])
def item_desc(category_name, item_name):
    db_session = DBSession()
    category = db_session.query(Category).filter_by(name=category_name).one()
    item = db_session.query(Item).filter_by(
        category_id=category.id).filter_by(name=item_name).one()
    if request.method == 'POST':
        for key, value in request.form.items():
            print("key: {0}, value: {1}".format(key, value))
        new_name = request.form['iname']
        if new_name:
            item.name = new_name
        new_desc = request.form['idesc']
        if new_desc:
            item.description = new_desc
        db_session.commit()
    return render_template('item_description.html',
                           item=item,
                           item_name=item.name,
                           category_name=category.name)

# adding a new item
@app.route("/catalog/<category_name>/new/", methods=['GET', 'POST'])
@authorized
def new_item(category_name):
    db_session = DBSession()
    if request.method == 'POST':
        category = db_session.query(Category).filter_by(
            name=category_name).one()
        newItem = Item(
            name=request.form['iname'],
            category=category, category_id=category.id,
            description=request.form['idesc'], user_id=session['gplus_id'])
        if item and item.user_id != session['user_id']:
            flash("Error")
            state = session['state']
            categories = db_session.query(Category)
            return render_template('home.html',
                                   categories=categories, STATE=state)
        else:
            db_session.add(newItem)
            db_session.commit()
            flash("new menu item created")
            return (catalog_desc(category.name))
    else:
        return render_template('new_item.html', category_name=category_name)

# Editing an item
@app.route("/catalog/<category_name>/<item_name>/edit/",
           methods=['GET', 'POST'])
@authorized
def edit_item(category_name, item_name):
    db_session = DBSession()
    category = db_session.query(Category).filter_by(
        name=category_name).one()
    item = db_session.query(Item).filter_by(
        category_id=category.id).filter_by(name=item_name).one()
    if item and item.user_id != session['user_id']:
        flash("Error")
        state = session['state']
        categories = db_session.query(Category)
        return render_template('home.html', categories=categories, STATE=state)
    else:
        return render_template('edit_description.html', category=category,
                               item=item, item_name=item.name,
                               category_name=category.name)


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
