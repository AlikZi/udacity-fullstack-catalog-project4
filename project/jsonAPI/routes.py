# Modules from Flask Library
from flask import Flask, render_template, request, flash, Blueprint
from flask import session as login_session
from flask import make_response, redirect, jsonify, url_for
# SQLAlchemy library to access database
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from project.models import Base, Category, Product, User

import random
import string
import httplib2
import json
import requests


jsonAPI = Blueprint('jsonAPI', __name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///furniturecatalog.db',
                       connect_args={'check_same_thread': False})
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

'''
JSON endpoints
'''

@jsonAPI.route('/catalog/json/')
def showAllJSON():
    """App route function to show Catalog Data in JSON."""
    # Obtain all categoris
    categories = session.query(Category).all()
    # Obtain all products
    products = session.query(Product).all()
    return jsonify(categories=[cat.serialize for cat in categories],
                   products=[prod.serialize for prod in products])


@jsonAPI.route('/categories/json/')
def showCategoriesJSON():
    """App route function to show Categories Data in JSON."""
    # Obtain all categoris
    categories = session.query(Category).all()
    return jsonify(categories=[cat.serialize for cat in categories])


@jsonAPI.route('/products/json/')
def showProductsJSON():
    """App route function to show Products Data in JSON."""
    # Obtain all products
    products = session.query(Product).all()
    return jsonify(products=[prod.serialize for prod in products])


@jsonAPI.route('/category/<int:cat_id>/json/')
def showCategoryJSON(cat_id):
    """App route function to show selected Category JSON."""
    # Obtain Category
    category = session.query(Category).filter_by(id=cat_id).one()
    return jsonify(category=[category.serialize])


@jsonAPI.route('/product/<int:prod_id>/json/')
def showProductJSON(prod_id):
    """App route function to show selected Product JSON."""
    # Obtain product
    product = session.query(Product).filter_by(id=prod_id).one()
    return jsonify(product=[product.serialize])

