from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Product, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


# Connect to Database and create database session
engine = create_engine('sqlite:///furniturecatalog.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Main page, show all categories
@app.route('/')
@app.route('/categories/')
def showCategories():
	categories = session.query(Category).all()
	return render_template('index.html', categories=categories)

@app.route('/categories/<int:cat_id>/')
def showCategoryProcucts(cat_id):
	categories = session.query(Category).all()
	category = session.query(Category).filter_by(id=cat_id).one()
	products = session.query(Product).filter_by(category_id=category.id).all()
	return render_template('category.html', products=products, categories=categories)






if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
