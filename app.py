from flask import Flask, render_template, url_for
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
    return render_template('item_description.html', category=row, items=x)


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
