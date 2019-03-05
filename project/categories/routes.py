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

# Authentification modules
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# Create Blueprint 'categories'
categories = Blueprint('categories', __name__)

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


@categories.route('/')
@categories.route('/categories/')
def showCategories():
    """App route function for main page to show all categories."""
    # Check if user is logged in
    isLogin = 'email' in login_session
    # All categories ordered by name
    categories = session.query(Category).order_by(Category.name).all()
    # Select recently added products
    latestProducts = (session.query(Product)
                      .order_by(Product.created_date.desc()).limit(8))
    return render_template('index.html', categories=categories,
                           isLogin=isLogin, latestProducts=latestProducts)


@categories.route('/categories/<int:cat_id>/')
def showCategoryProducts(cat_id):
    """App route function to show Products of the selected Category."""
    # Check if user is logged in
    isLogin = 'email' in login_session
    # All categories ordered by name
    categories = session.query(Category).order_by(Category.name).all()
    # Get category that is selected to be shown
    category = session.query(Category).filter_by(id=cat_id).one()
    # Check if user is Creator of Category
    isCreator = False
    if isLogin:
        isCreator = login_session['email'] == category.user.email
    # Count how many products selected Category have
    countProducts = (session.query(Product)
                     .filter_by(category_id=cat_id).count())
    # Get all products from selected Category
    products = session.query(Product).filter_by(category_id=category.id).all()
    return render_template('category.html', products=products,
                           categories=categories, category=category,
                           isLogin=isLogin, countProducts=countProducts,
                           isCreator=isCreator)


@categories.route('/addcategory/', methods=['GET', 'POST'])
def addCategory():
    """App route function to add new Category to the Category Table."""
    if 'email' not in login_session:
        return redirect('/login')
    # Check if user is logged in and save the result in isLogin
    isLogin = 'email' in login_session
    # All categories ordered by name
    categories = session.query(Category).order_by(Category.name).all()
    if request.method == 'POST':
        if request.form['name'] == '':
            flash("Please, enter Category Name")
            return render_template('addcategory.html',
                                   categories=categories,
                                   isLogin=isLogin)
        newCategory = Category(name=request.form['name'],
                               user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        flash('New Category {} Successfully Created'.format(newCategory.name))
        return redirect(url_for('categories.showCategories'))
    else:
        return render_template('addcategory.html',
                               categories=categories,
                               isLogin=isLogin)


@categories.route('/editcategory/<int:cat_id>/', methods=['GET', 'POST'])
def editCategory(cat_id):
    """App route function to edit existing Category."""
    # If user is not logged in, inform him about it and redirect
    if 'email' not in login_session:
        flash("You need to Log In if you want to edit")
        return redirect('/categories')
    # Check if user is logged in and save the result in isLogin
    isLogin = 'email' in login_session
    # Get category that is selected to be edited
    categoryToEdit = session.query(Category).filter_by(id=cat_id).one()
    # Check if user is Creator, if not inform that he cannot
    # do changes
    if not login_session['email'] == categoryToEdit.user.email:
        flash("You need to be Creator of the category to be able to edit")
        return redirect('/categories')
    # All categories ordered by name
    categories = session.query(Category).order_by(Category.name).all()
    if request.method == 'POST':
        if request.form['name']:
            categoryToEdit.name = request.form['name']
        else:
            flash('Please, enter category name.')
            return render_template('editcategory.html',
                                   categories=categories,
                                   isLogin=isLogin,
                                   categoryToEdit=categoryToEdit)
        session.add(categoryToEdit)
        session.commit()
        flash('You successfully \
              updated category to {}'.format(categoryToEdit.name))
        return redirect(url_for('categories.showCategoryProducts', cat_id=cat_id))
    else:
        return render_template('editcategory.html', categories=categories,
                               isLogin=isLogin, categoryToEdit=categoryToEdit)


@categories.route('/deletecategory/<int:cat_id>/', methods=['GET', 'POST'])
def deleteCategory(cat_id):
    """App route function to delete existing Category"""
    # If user is not logged in, inform him about it and redirect
    if 'email' not in login_session:
        flash("You need to Log In if you want to delete the category.")
        return redirect('/categories')
    # Check if user is logged in and save the result in isLogin
    isLogin = 'email' in login_session
    # Get category that is selected to be edited
    categoryToDelete = session.query(Category).filter_by(id=cat_id).one()
    # Check if user is Creator, if not inform that he cannot
    # do changes
    if not login_session['email'] == categoryToDelete.user.email:
        flash("You need to be a Creator of the category\
               to be able to delete it")
        return redirect('/categories')
    # All categories ordered by name
    categories = session.query(Category).order_by(Category.name).all()
    # Check for method and do appropriate. If 'POST' -> delete Category,
    # if 'GET' -> render 'deletecategory.html'
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        flash('You successfully deleted \
              category "{}"'.format(categoryToDelete.name))
        return redirect(url_for('categories.showCategories'))
    else:
        return render_template('deletecategory.html',
                               categories=categories,
                               isLogin=isLogin,
                               categoryToDelete=categoryToDelete)
