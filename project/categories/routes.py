# Modules from Flask Library
from flask import Flask, render_template, request, flash, Blueprint
from flask import session as login_session
from flask import make_response, redirect, jsonify, url_for
# Access database
from project.models import Category, Product, User
from project.db import DBConnector
# Services
from project.services.categories import CategoryService
from project.services.auth import AuthService
from project.services.products import ProductService

import random
import string
import httplib2
import json
import requests


# Create Blueprint 'categories'
categories = Blueprint('categories', __name__)

# Connect to the database, create session
session = DBConnector().get_session()

# Instantiate services
category_service = CategoryService()
product_service = ProductService()
auth_service = AuthService()


@categories.route('/')
@categories.route('/categories/')
def showCategories():
    """App route function for main page to show all categories."""
    return render_template('index.html',
                           categories=category_service.get_all_categories(),
                           isLogin=auth_service.is_user_authorized(),
                           latestProducts=(product_service
                                           .get_latest_products(8)))


@categories.route('/categories/<int:cat_id>/')
def showCategoryProducts(cat_id):
    """App route function to show Products of the selected Category."""
    isLogin = auth_service.is_user_authorized()
    # Pick category selected by user
    category = category_service.get_category_by_id(cat_id)
    # Check if user is Creator of Category
    isCreator = False
    if isLogin:
        isCreator = login_session['email'] == category.user.email
    return render_template('category.html',
                           products=(product_service
                                     .get_products_by_cat_id(cat_id)),
                           categories=category_service.get_all_categories(),
                           category=category,
                           isLogin=isLogin,
                           countProducts=(product_service
                                          .products_count(cat_id)),
                           isCreator=isCreator)


@categories.route('/addcategory/', methods=['GET', 'POST'])
def addCategory():
    """App route function to add new Category to the Category Table."""
    if 'email' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name'] == '':
            flash("Please, enter Category Name")
            return render_template('addcategory.html',
                                   categories=(category_service
                                               .get_all_categories()),
                                   isLogin=auth_service.is_user_authorized())
        newCategory = Category(name=request.form['name'],
                               user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        flash('New Category {} Successfully Created'.format(newCategory.name))
        return redirect(url_for('categories.showCategories'))
    else:
        return render_template('addcategory.html',
                               categories=(category_service
                                           .get_all_categories()),
                               isLogin=auth_service.is_user_authorized())


@categories.route('/editcategory/<int:cat_id>/',
                  methods=['GET', 'POST'])
def editCategory(cat_id):
    """App route function to edit existing Category."""
    # If user is not logged in, inform him about it and redirect
    if 'email' not in login_session:
        flash("You need to Log In if you want to edit")
        return redirect('/categories')
    # Get category that is selected to be edited
    categoryToEdit = session.query(Category).filter_by(id=cat_id).one()
    # Check if user is Creator, if not inform that he cannot
    # do changes
    if not login_session['email'] == categoryToEdit.user.email:
        flash("You need to be Creator of the category to be able to edit")
        return redirect('/categories')
    if request.method == 'POST':
        if request.form['name']:
            categoryToEdit.name = request.form['name']
        else:
            flash('Please, enter category name.')
            return render_template('editcategory.html',
                                   categories=(category_service
                                               .get_all_categories()),
                                   isLogin=auth_service.is_user_authorized(),
                                   categoryToEdit=categoryToEdit)
        session.add(categoryToEdit)
        session.commit()
        flash('You successfully \
              updated category to {}'.format(categoryToEdit.name))
        return redirect(url_for('categories.showCategoryProducts',
                                cat_id=cat_id))
    else:
        return render_template('editcategory.html',
                               categories=(category_service
                                           .get_all_categories()),
                               isLogin=auth_service.is_user_authorized(),
                               categoryToEdit=categoryToEdit)


@categories.route('/deletecategory/<int:cat_id>/', methods=['GET', 'POST'])
def deleteCategory(cat_id):
    """App route function to delete existing Category"""
    # If user is not logged in, inform him about it and redirect
    if 'email' not in login_session:
        flash("You need to Log In if you want to delete the category.")
        return redirect('/categories')
    # Get category that is selected to be edited
    categoryToDelete = session.query(Category).filter_by(id=cat_id).one()
    # Check if user is Creator, if not inform that he cannot
    # do changes
    if not login_session['email'] == categoryToDelete.user.email:
        flash("You need to be a Creator of the category\
               to be able to delete it")
        return redirect('/categories')
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
                               categories=(category_service
                                           .get_all_categories()),
                               isLogin=auth_service.is_user_authorized(),
                               categoryToDelete=categoryToDelete)
