from flask import Flask, render_template, url_for, request, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog_database_setup import Base, Categories, item
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


app = Flask(__name__)


@app.route("/")
def home():
    session = DBSession()
    categories = session.query(Categories)
    return render_template('home.html', categories=categories)


@app.route("/catalog/<name>/items/", methods=['GET'])
def catalog_desc(name):
    session = DBSession()
    row = []
    categories = session.query(Categories)
    for row in session.query(Categories).filter_by(name=name).all():
        print(row)
    x = session.query(item).filter_by(item_id=row.id).all()
    print(x)
    return render_template('category.html', category=categories, items=x)


@app.route("/catalog/<name>/<item_name>", methods=['GET'])
def item_desc(name, item_name):
    session = DBSession()
    row = []
    for row in session.query(Categories).filter_by(name=name).all():
        print(row)
    x = session.query(item).filter_by(
        item_id=row.id).filter_by(name=item_name).all()
    print(x)
    return render_template('item_description.html', category=row, items=x, name=item_name, n=name)


@app.route("/login", methods=['POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = "Invalid Credentials, Please try again"
        else:
            render_template('home.html')
    else:
        render_template('login.html', error=error)


@app.route("/catalog/<name>/<item_name>/edit", methods=['GET', 'POST'])
def edit_item(name, item_name):
    session = DBSession()
    row = []
    for row in session.query(Categories).filter_by(name=name).all():
        print(row)
    x = session.query(item).filter_by(
        item_id=row.id).filter_by(name=item_name).all()
    print(x)
    if request.method == 'POST':
        print("Hello")
        if request.form['desc']:
            desc = request.form['desc']
            print(desc)

            session.add(desc)
            session.commit()
            return (redirect(url_for('item_description.html', category=row, items=x, name=item_name, n=name)))
    else:
        return render_template('edit_description.html', category=row, items=x, name=item_name, n=name)


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
