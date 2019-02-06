'''
Project 4 for Udacity Fullstack Nanodegree
Author: Aleksandr Zonis
'''

# Modules from Flask Library
from flask import Flask, render_template, request, flash
from flask import session as login_session
from flask import make_response, redirect, jsonify, url_for
# SQLAlchemy library to access database
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Product, User

import random
import string
import httplib2
import json
import requests

# Authentification modules
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"


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


# Login Page
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
     # All categories ordered by name
    categories = session.query(Category).order_by(Category.name).all()
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state, categories=categories,
                           CLIENT_ID=CLIENT_ID)


# Main page, show all categories
@app.route('/')
@app.route('/categories/')
def showCategories():
    # Check if user is logged in
    isLogin = 'email' in login_session
    # All categories ordered by name
    categories = session.query(Category).order_by(Category.name).all()
    # Select recently added products
    latestProducts = (session.query(Product)
                      .order_by(Product.created_date.desc()).limit(8))
    return render_template('index.html', categories=categories,
                           isLogin=isLogin, latestProducts=latestProducts)


# Show Products of the selected Category
@app.route('/categories/<int:cat_id>/')
def showCategoryProducts(cat_id):
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


# Show selected product
@app.route('/categories/<int:cat_id>/<int:prod_id>/')
def showProduct(cat_id, prod_id):
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


# Add new Category to the Category Table
@app.route('/addcategory/', methods=['GET', 'POST'])
def addCategory():
    # If user is not logged in, inform him about it and redirect
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
        return redirect(url_for('showCategories'))
    else:
        return render_template('addcategory.html',
                               categories=categories,
                               isLogin=isLogin)


# Add new Product to the Product list
@app.route('/addproduct/', methods=['GET', 'POST'])
def addProduct():
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
        return redirect(url_for('showCategoryProducts',
                                cat_id=newProduct.category_id))
    else:
        return render_template('addproduct.html',
                               categories=categories, isLogin=isLogin)


# Edit existing Category
@app.route('/editcategory/<int:cat_id>/', methods=['GET', 'POST'])
def editCategory(cat_id):
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
            session.add(categoryToEdit)
            session.commit()
            flash('You successfully \
                  updated category to {}'.format(categoryToEdit.name))
            return redirect(url_for('showCategoryProducts', cat_id=cat_id))
    else:
        return render_template('editcategory.html', categories=categories,
                               isLogin=isLogin, categoryToEdit=categoryToEdit)


# Delete existing Category
@app.route('/deletecategory/<int:cat_id>/', methods=['GET', 'POST'])
def deleteCategory(cat_id):
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
        return redirect(url_for('showCategories'))
    else:
        return render_template('deletecategory.html',
                               categories=categories,
                               isLogin=isLogin,
                               categoryToDelete=categoryToDelete)


# Edit existing Product
@app.route('/editproduct/<int:cat_id>/<int:prod_id>/', methods=['GET', 'POST'])
def editProduct(cat_id, prod_id):
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
        return redirect(url_for('showProduct', cat_id=cat_id, prod_id=prod_id))
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
        return redirect(url_for('showProduct', cat_id=cat_id, prod_id=prod_id))
    else:
        return render_template('editproduct.html', categories=categories,
                               isLogin=isLogin, category=category,
                               productToEdit=productToEdit)


# Delete existing product
@app.route('/deleteproduct/<int:cat_id>/<int:prod_id>/',
           methods=['GET', 'POST'])
def deleteProduct(cat_id, prod_id):
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
        return redirect(url_for('showProduct', cat_id=cat_id, prod_id=prod_id))

    # All categories ordered by name
    categories = session.query(Category).order_by(Category.name).all()

    # Get category that is selected to be shown
    category = session.query(Category).filter_by(id=cat_id).one()
    if request.method == 'POST':
        session.delete(productToDelete)
        session.commit()
        flash('You successfully deleted \
              product "{}"'.format(productToDelete.name))
        return redirect(url_for('showCategoryProducts', cat_id=cat_id))
    else:
        return render_template('deleteproduct.html', categories=categories,
                               isLogin=isLogin, category=category,
                               productToDelete=productToDelete)


'''
JSON endpoints
'''


# Show Catalog Data in JSON
@app.route('/catalog/json/')
def showAllJSON():
    # Obtain all categoris
    categories = session.query(Category).all()
    # Obtain all products
    products = session.query(Product).all()
    return jsonify(categories=[cat.serialize for cat in categories],
                   products=[prod.serialize for prod in products])


# Show Categories Data in JSON
@app.route('/categories/json/')
def showCategoriesJSON():
    # Obtain all categoris
    categories = session.query(Category).all()
    return jsonify(categories=[cat.serialize for cat in categories])


# Show Products Data in JSON
@app.route('/products/json/')
def showProductsJSON():
    # Obtain all products
    products = session.query(Product).all()
    return jsonify(products=[prod.serialize for prod in products])


@app.route('/category/<int:cat_id>/json/')
def showCategoryJSON(cat_id):
    # Obtain Category
    category = session.query(Category).filter_by(id=cat_id).one()
    return jsonify(category=[category.serialize])


@app.route('/product/<int:prod_id>/json/')
def showProductJSON(prod_id):
    # Obtain product
    product = session.query(Product).filter_by(id=prod_id).one()
    return jsonify(product=[product.serialize])


# Connect via Google Account and fetch User info
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
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
    h = requests.get(url=url)
    result = json.loads(h.text)
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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user \
                                            is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("You are now logged in as %s" % login_session['username'])
    print("done!")
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Disconnect user
@app.route('/gdisconnect')
def gdisconnect():
    # Check if user is connected,
    # only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        flash("Current user not connected")
        return redirect(url_for('showCategories'))
    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    # Delete all login_session info
    del login_session['gplus_id']
    del login_session['access_token']
    del login_session['username']
    del login_session['email']
    del login_session['user_id']
    del login_session['provider']
    flash("You have successfully been logged out.")
    return redirect(url_for('showCategories'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
