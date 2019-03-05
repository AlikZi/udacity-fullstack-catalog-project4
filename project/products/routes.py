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


products = Blueprint('products', __name__)

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


@products.route('/categories/<int:cat_id>/<int:prod_id>/')
def showProduct(cat_id, prod_id):
    """App route function to show selected product."""
    # Check if user is logged in and save the result in isLogin
    isLogin = 'email' in login_session
    # All categories ordered by name
    categories = session.query(Category).order_by(Category.name).all()
    # Get category that is selected to be shown
    category = session.query(Category).filter_by(id=cat_id).one()
    product = session.query(Product).filter_by(id=prod_id).one()
    # Check if user is Creator of Category or Product
    isCreator = False
    if isLogin:
        isCreator = (login_session['email'] == category.user.email or
                     login_session['email'] == product.user.email)
    # Get the selected product
    product = session.query(Product).filter_by(id=prod_id).one()
    return render_template('product.html', categories=categories,
                           category=category, product=product,
                           isLogin=isLogin, isCreator=isCreator)


@products.route('/addproduct/', methods=['GET', 'POST'])
def addProduct():
    """App route function to add new Product to the Product list."""
    # If user is not logged in, inform him about it and redirect
    if 'email' not in login_session:
        return redirect('/login')
    # Check if user is logged in and save the result in isLogin
    isLogin = 'email' in login_session
    # All categories ordered by name
    categories = session.query(Category).order_by(Category.name).all()
    if request.method == 'POST':
        # Check if all the fields are filled out
        if request.form['name'] == '':
            flash("Please, enter product name. \
                  Make sure you fill out all the fields")
            return render_template('addproduct.html',
                                   categories=categories,
                                   isLogin=isLogin)
        if request.form['image_url'] == '':
            flash("Please, enter product image(link of the image). \
                   Make sure you fill out all the fields")
            return render_template('addproduct.html',
                                   categories=categories,
                                   isLogin=isLogin)
        if request.form['product_url'] == '':
            flash("Please, enter product URL. \
                  Make sure you fill out all the fields")
            return render_template('addproduct.html',
                                   categories=categories,
                                   isLogin=isLogin)
        if request.form['description'] == '':
            flash('Please, enter product description. \
                  Make sure you fill out all the fields')
            return render_template('addproduct.html',
                                   categories=categories,
                                   isLogin=isLogin)

        category = (session.query(Category)
                    .filter_by(name=request.form['category_name']).one())
        newProduct = Product(name=request.form['name'],
                             description=request.form['description'],
                             image_url=request.form['image_url'],
                             product_url=request.form['product_url'],
                             category_id=category.id,
                             user_id=login_session['user_id'])
        session.add(newProduct)
        session.commit()
        flash('New Product {} Successfully Created'.format(newProduct.name))
        return redirect(url_for('categories.showCategoryProducts',
                                cat_id=newProduct.category_id))
    else:
        return render_template('addproduct.html',
                               categories=categories, isLogin=isLogin)


@products.route('/editproduct/<int:cat_id>/<int:prod_id>/', methods=['GET', 'POST'])
def editProduct(cat_id, prod_id):
    """App route function to edit existing Product."""
    # If user is not logged in, inform him about it and redirect
    if 'email' not in login_session:
        flash("You need to Log In if you want to edit")
        return redirect('/login')
    # Check if user is logged in and save the result in isLogin
    isLogin = 'email' in login_session
    # Get Product that user wants to edit
    productToEdit = session.query(Product).filter_by(id=prod_id).one()
    # Check if user is Creator, if not inform that he cannot
    # do changes
    if not login_session['email'] == productToEdit.user.email:
        flash("You need to be a Creator of the Product to edit it")
        return redirect(url_for('products.showProduct', cat_id=cat_id, prod_id=prod_id))
    # All categories ordered by name
    categories = session.query(Category).order_by(Category.name).all()
    # Get category that is selected to be shown
    category = session.query(Category).filter_by(id=cat_id).one()
    if request.method == 'POST':
        if request.form['name']:
            productToEdit.name = request.form['name']
        if request.form['image_url']:
            productToEdit.image_url = request.form['image_url']
        if request.form['product_url']:
            productToEdit.product_url = request.form['product_url']
        if request.form['description']:
            productToEdit.description = request.form['description']
        session.add(productToEdit)
        session.commit()
        flash('You successfully edited product')
        return redirect(url_for('products.showProduct', cat_id=cat_id, prod_id=prod_id))
    else:
        return render_template('editproduct.html', categories=categories,
                               isLogin=isLogin, category=category,
                               productToEdit=productToEdit)



@products.route('/deleteproduct/<int:cat_id>/<int:prod_id>/',
           methods=['GET', 'POST'])
def deleteProduct(cat_id, prod_id):
    """App route function to delete existing product."""
    # If user is not logged in, inform him about it and redirect
    if 'email' not in login_session:
        flash("You need to Log In if you want to delete product")
        return redirect('/login')

    # Check if user is logged in and save the result in isLogin
    isLogin = 'email' in login_session

    # Get the Product that User wants to delete
    productToDelete = session.query(Product).filter_by(id=prod_id).one()

    # Check if user is Creator, if not inform that he cannot
    # do changes
    if not login_session['email'] == productToDelete.user.email:
        flash("You need to be a Creator of the Product to delete it")
        return redirect(url_for('products.showProduct', cat_id=cat_id, prod_id=prod_id))

    # All categories ordered by name
    categories = session.query(Category).order_by(Category.name).all()

    # Get category that is selected to be shown
    category = session.query(Category).filter_by(id=cat_id).one()
    if request.method == 'POST':
        session.delete(productToDelete)
        session.commit()
        flash('You successfully deleted \
              product "{}"'.format(productToDelete.name))
        return redirect(url_for('categories.showCategoryProducts', cat_id=cat_id))
    else:
        return render_template('deleteproduct.html', categories=categories,
                               isLogin=isLogin, category=category,
                               productToDelete=productToDelete)
