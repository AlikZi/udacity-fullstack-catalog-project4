# Modules from Flask Library
from flask import Flask, render_template, request, flash, Blueprint
from flask import session as login_session
from flask import make_response, redirect, jsonify, url_for
# Access database
from project.models import Category, Product, User
from project.db import session

# Services
from project.services.categories import CategoryService
from project.services.auth import AuthService
from project.services.products import ProductService

import random
import string
import httplib2
import json
import requests

products = Blueprint('products', __name__)

# Instantiate services
category_service = CategoryService()
product_service = ProductService()
auth_service = AuthService()


@products.route('/categories/<int:category_id>/<int:product_id>/')
def showProduct(category_id, product_id):
    """App route function to show selected product."""
    # Check if user is logged in and save the result in isLogin
    isLogin = auth_service.is_user_authorized()
    # Get category that is selected to be shown
    category = category_service.get_category_by_id(category_id)
    product = product_service.get_product_by_id(product_id)
    # Check if user is Creator of Category or Product
    isCreator = False
    if isLogin:
        isCreator = (login_session['email'] == category.user.email or
                     login_session['email'] == product.user.email)
    return render_template('product.html',
                           categories=category_service.get_all_categories(),
                           category=category, product=product,
                           isLogin=isLogin, isCreator=isCreator)


@products.route('/addproduct/', methods=['GET', 'POST'])
def addProduct():
    """App route function to add new Product to the Product list."""
    # If user is not logged in, inform him about it and redirect
    if 'email' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        # Check if all the fields are filled out
        if request.form['name'] == '':
            flash("Please, enter product name. \
                  Make sure you fill out all the fields")
            return render_template('addproduct.html',
                                   categories=(category_service
                                               .get_all_categories()),
                                   isLogin=auth_service.is_user_authorized())
        if request.form['image_url'] == '':
            flash("Please, enter product image(link of the image). \
                   Make sure you fill out all the fields")
            return render_template('addproduct.html',
                                   categories=(category_service
                                               .get_all_categories()),
                                   isLogin=auth_service.is_user_authorized())
        if request.form['product_url'] == '':
            flash("Please, enter product URL. \
                  Make sure you fill out all the fields")
            return render_template('addproduct.html',
                                   categories=(category_service
                                               .get_all_categories()),
                                   isLogin=auth_service.is_user_authorized())
        if request.form['description'] == '':
            flash('Please, enter product description. \
                  Make sure you fill out all the fields')
            return render_template('addproduct.html',
                                   categories=(category_service
                                               .get_all_categories()),
                                   isLogin=auth_service.is_user_authorized())

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
                                category_id=newProduct.category_id))
    else:
        return render_template('addproduct.html',
                               categories=(category_service
                                           .get_all_categories()),
                               isLogin=auth_service.is_user_authorized())


@products.route('/editproduct/<int:category_id>/<int:product_id>/',
                methods=['GET', 'POST'])
def editProduct(category_id, product_id):
    """App route function to edit existing Product."""
    # If user is not logged in, inform him about it and redirect
    if 'email' not in login_session:
        flash("You need to Log In if you want to edit")
        return redirect('/login')
    # Get Product that user wants to edit
    productToEdit = product_service.get_product_by_id(product_id)
    # Check if user is Creator, if not inform that he cannot
    # do changes
    if not login_session['email'] == productToEdit.user.email:
        flash("You need to be a Creator of the Product to edit it")
        return redirect(url_for('products.showProduct',
                                category_id=category_id, product_id=product_id))
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
        return redirect(url_for('products.showProduct',
                                category_id=category_id, product_id=product_id))
    else:
        return render_template('editproduct.html',
                               categories=(category_service
                                           .get_all_categories()),
                               isLogin=auth_service.is_user_authorized(),
                               category=(category_service
                                         .get_category_by_id(category_id)),
                               productToEdit=productToEdit)


@products.route('/deleteproduct/<int:category_id>/<int:product_id>/',
                methods=['GET', 'POST'])
def deleteProduct(category_id, product_id):
    """App route function to delete existing product."""
    # If user is not logged in, inform him about it and redirect
    if 'email' not in login_session:
        flash("You need to Log In if you want to delete product")
        return redirect('/login')
    # Get the Product that User wants to delete
    productToDelete = product_service.get_product_by_id(product_id)
    # Check if user is Creator, if not inform that he cannot
    # do changes
    if not login_session['email'] == productToDelete.user.email:
        flash("You need to be a Creator of the Product to delete it")
        return redirect(url_for('products.showProduct',
                                category_id=category_id, product_id=product_id))
    if request.method == 'POST':
        session.delete(productToDelete)
        session.commit()
        flash('You successfully deleted \
              product "{}"'.format(productToDelete.name))
        return redirect(url_for('categories.showCategoryProducts',
                                category_id=category_id))
    else:
        return render_template('deleteproduct.html',
                               categories=(category_service
                                           .get_all_categories()),
                               isLogin=auth_service.is_user_authorized(),
                               category=(category_service
                                         .get_category_by_id(category_id)),
                               productToDelete=productToDelete)
