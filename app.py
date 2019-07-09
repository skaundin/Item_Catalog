from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, abort, json, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog_database_setup import Base, Categories, item
from flask_httpauth import HTTPBasicAuth
# NEW IMPORTS
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import random
import string
from flask import make_response
import requests
from gauth import authorized

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

auth = HTTPBasicAuth()

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
    x = db_session.query(item).all()
    return jsonify(items=[i.serialize for i in x])


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
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    credentials.access_token_expired
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    output = ''
    output += '<h1>Welcome, '
    output += session['username']
    output += '!</h1>'
    output += '<img src="'
    output += session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % session['username'])
    print("done!")
    return output

# home page
@app.route("/")
def home():
    db_session = DBSession()
    categories = db_session.query(Categories)
    return render_template('home.html', categories=categories)

# login page
@app.route("/login")
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    session['state'] = state
    # return "The current session state is %s" % session['state']
    return render_template('login.html', STATE=state)

# deleteing an item
@app.route("/catalog/<category_name>/<item_name>/delete", methods=['GET', 'POST'])
def delete_item(category_name, item_name):
    db_session = DBSession()
    rows = db_session.query(Categories).filter_by(name=category_name).all()
    print(rows)
    deletedItem = db_session.query(item).filter_by(
        item_id=rows[0].id).filter_by(name=item_name).one()
    if request.method == 'POST':
        db_session.delete(deletedItem)
        db_session.commit()
        flash("Item has been deleted")

        return home()
    else:
        return home()

# catalog list
@app.route("/catalog/<category_name>/items/", methods=['GET'])
def catalog_desc(category_name):
    db_session = DBSession()
    row = []
    categories = db_session.query(Categories)
    for row in db_session.query(Categories).filter_by(name=category_name).all():
        print(row)
    x = db_session.query(item).filter_by(item_id=row.id).all()
    print(x)
    return render_template('category.html', items=x, category_name=category_name, categories=categories)

# description of an item for a category
@app.route("/catalog/<category_name>/<item_name>/", methods=['GET'])
def item_desc(category_name, item_name):
    db_session = DBSession()
    row = []
    for row in db_session.query(Categories).filter_by(name=category_name).all():
        print(row)
    x = db_session.query(item).filter_by(
        item_id=row.id).filter_by(name=item_name).all()
    print(x)
    return render_template('item_description.html', category=row, items=x, item_name=item_name, category_name=category_name)

# adding a new item
@app.route("/catalog/<category_name>/new/", methods=['GET', 'POST'])
def new_item(category_name):
    db_session = DBSession()
    if request.method == 'POST':
        newItem = item(
            name=request.form['iname'], items=Categories(name=category_name), description=request.form['idesc'])
        db_session.add(newItem)
        db_session.commit()
        flash("new menu item created")
        return (catalog_desc(category_name))
    else:
        return render_template('new_item.html', category_name=category_name)

# updating an item
@app.route("/catalog/<category_name>/<item_name>/edit/", methods=['GET', 'POST'])
def edit_item(category_name, item_name):
    db_session = DBSession()
    rows = db_session.query(Categories).filter_by(name=category_name).all()
    print(rows)
    x = db_session.query(item).filter_by(
        item_id=rows[0].id).filter_by(name=item_name).all()
    print(x)
    return render_template('edit_description.html', category=rows[0], items=x, item_name=item_name, category_name=category_name)

# displaying the items for a category
@app.route("/catalog/<category_name>/<item_name>", methods=['POST'])
def display_item(category_name, item_name):
    db_session = DBSession()
    row = []
    x = []
    for row in db_session.query(Categories).filter_by(name=category_name).all():
        print(row)
        x = db_session.query(item).filter_by(
            item_id=row.id).filter_by(name=item_name).all()
    if request.method == 'POST':
        for key, value in request.form.items():
            print("key: {0}, value: {1}".format(key, value))
        # print(category_name)
        # print(item_name)
        # print(request.form['category'])
        if request.form['idesc']:
            for j in x:
                print(j.name)
                print(j.description)
                j.description = request.form['idesc']

                db_session.add(j)
                db_session.commit()
                return item_desc(category_name, item_name)


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
