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


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"


# Connect to Database and create database session
engine = create_engine('sqlite:///furniturecatalog.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    categories = session.query(Category).all()
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state, categories=categories,
    						CLIENT_ID=CLIENT_ID)


# Main page, show all categories
@app.route('/')
@app.route('/categories/')
def showCategories():
    isLogin = 'email' in login_session
    categories = session.query(Category).all()
    latestProducts = session.query(Product).order_by(Product.created_date.desc()).limit(8)
    return render_template('index.html', categories=categories, isLogin=isLogin, latestProducts=latestProducts)

@app.route('/categories/<int:cat_id>/')
def showCategoryProducts(cat_id):
    isLogin = 'email' in login_session
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=cat_id).one()
    countProducts = session.query(Product).filter_by(category_id=cat_id).count()
    products = session.query(Product).filter_by(category_id=category.id).all()
    return render_template('category.html', products=products, 
                           categories=categories, category=category,
                           isLogin=isLogin, countProducts=countProducts)

@app.route('/categories/<int:cat_id>/<int:prod_id>/')
def showProduct(cat_id, prod_id):
    isLogin = 'email' in login_session
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=cat_id).one()
    product = session.query(Product).filter_by(id=prod_id).one()
    return render_template('product.html', categories=categories,
                            category=category, product=product,
                            isLogin=isLogin)


# Add new Category to the Category Table
@app.route('/addcategory/', methods=['GET', 'POST'])
def addCategory():
    if 'email' not in login_session:
        return redirect('/login')
    isLogin = 'email' in login_session
    categories = session.query(Category).all()
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        flash('New Category {} Successfully Created'.format(newCategory.name))
        return redirect(url_for('showCategories'))
    else:
        return render_template('addcategory.html', categories=categories, isLogin=isLogin)


# Add new Product to the Product list
@app.route('/addproduct/', methods=['GET', 'POST'])
def addProduct():
    if 'email' not in login_session:
        return redirect('/login')
    isLogin = 'email' in login_session
    categories = session.query(Category).all()
    if request.method == 'POST':
        category=session.query(Category).filter_by(name=request.form['category_name']).one()
        newProduct = Product(name = request.form['name'], description=request.form['description'],
                             image_url=request.form['image_url'], product_url=request.form['product_url'],
                             category_id=category.id)
        session.add(newProduct)
        session.commit()
        flash('New Product {} Successfully Created'.format(newProduct.name))
        return redirect(url_for('showCategories'))
    else:
        return render_template('addproduct.html', categories=categories, isLogin=isLogin)

# Edit existing Category
@app.route('/editcategory/<int:cat_id>/', methods=['GET', 'POST'])
def editCategory(cat_id):
    if 'email' not in login_session:
    	flash("You need to Log In if you want to edit.")
        return redirect('/categories')
    isLogin = 'email' in login_session
    categories = session.query(Category).all()
    categoryToEdit = session.query(Category).filter_by(id=cat_id).one()
    if request.method == 'POST':
        if request.form['name']:
            categoryToEdit.name = request.form['name']
            session.add(categoryToEdit)
            session.commit()
            flash('You successfully updated category to {}'.format(categoryToEdit.name))
            return redirect(url_for('showCategoryProducts', cat_id=cat_id))
    else:
        return render_template('editcategory.html', categories=categories,
                                isLogin=isLogin, categoryToEdit=categoryToEdit)


# Delete existing Category
@app.route('/deletecategory/<int:cat_id>/', methods=['GET', 'POST'])
def deleteCategory(cat_id):
    if 'email' not in login_session:
    	flash('You need to Log In, if you want to delete Category')
        return redirect('/login')
    isLogin = 'email' in login_session
    categories = session.query(Category).all()
    categoryToDelete = session.query(Category).filter_by(id=cat_id).one()
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        flash('You successfully deleted category "{}"'.format(categoryToDelete.name))
        return redirect(url_for('showCategories'))
    else:
        return render_template('deletecategory.html', categories=categories,
                                isLogin=isLogin, categoryToDelete=categoryToDelete)


# Edit existing Product
@app.route('/editproduct/<int:cat_id>/<int:prod_id>/', methods=['GET', 'POST'])
def editProduct(cat_id, prod_id):
    if 'email' not in login_session:
    	flash("You need to Log In if you want to edit.")
        return redirect('/categories')
    isLogin = 'email' in login_session
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=cat_id).one()
    productToEdit = session.query(Product).filter_by(id=prod_id).one()
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
@app.route('/deleteproduct/<int:cat_id>/<int:prod_id>', methods=['GET', 'POST'])
def deleteProduct(cat_id, prod_id):
    if 'email' not in login_session:
    	flash("You need to Log In if you want to delete Product.")
        return redirect('/login')
    isLogin = 'email' in login_session
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=cat_id).one()
    productToDelete = session.query(Product).filter_by(id=prod_id).one()
    if request.method == 'POST':
    	session.delete(productToDelete)
    	session.commit()
    	flash('You successfully deleted product "{}"'.format(productToDelete.name))
        return redirect(url_for('showCategoryProducts', cat_id=cat_id))
    else:
    	return render_template('deleteproduct.html', categories=categories,
                                isLogin=isLogin, category=category, 
                                productToDelete=productToDelete)



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
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
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
    print "done!"
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


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        flash("Current user not connected")
        return redirect(url_for('showCategories'))
    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
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
