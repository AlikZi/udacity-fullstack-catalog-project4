# Modules from Flask Library
from flask import Flask, render_template, request, flash, Blueprint
from flask import session as login_session
from flask import make_response, redirect, jsonify, url_for
# Access database
from project.models import Category, Product, User
from project.db import DBConnector
# Services
from project.services.categories import CategoryService
from project.services.products import ProductService

import random
import string
import httplib2
import json
import requests


jsonAPI = Blueprint('jsonAPI', __name__)

# Connect to the database, create session
session = DBConnector().get_session()

# Instantiate services
category_service = CategoryService()
product_service = ProductService()

'''
JSON endpoints
'''


@jsonAPI.route('/catalog/json/')
def showAllJSON():
    """App route function to show Catalog Data in JSON."""
    # Obtain all categoris
    categories = category_service.get_all_categories()
    # Obtain all products
    products = product_service.get_all_products()
    return jsonify(categories=[cat.serialize for cat in categories],
                   products=[prod.serialize for prod in products])


@jsonAPI.route('/categories/json/')
def showCategoriesJSON():
    """App route function to show Categories Data in JSON."""
    # Obtain all categoris
    categories = category_service.get_all_categories()
    return jsonify(categories=[cat.serialize for cat in categories])


@jsonAPI.route('/products/json/')
def showProductsJSON():
    """App route function to show Products Data in JSON."""
    # Obtain all products
    products = product_service.get_all_products()
    return jsonify(products=[prod.serialize for prod in products])


@jsonAPI.route('/category/<int:cat_id>/json/')
def showCategoryJSON(cat_id):
    """App route function to show selected Category JSON."""
    # Obtain Category
    category = category_service.get_category_by_id(cat_id)
    return jsonify(category=[category.serialize])


@jsonAPI.route('/product/<int:prod_id>/json/')
def showProductJSON(prod_id):
    """App route function to show selected Product JSON."""
    # Obtain product
    product = get_product_by_id(prod_id)
    return jsonify(product=[product.serialize])
