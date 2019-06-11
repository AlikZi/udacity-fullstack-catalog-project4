# Modules from Flask Library
from flask import Flask, render_template, request, flash, Blueprint
from flask import session as login_session
from flask import make_response, redirect, jsonify, url_for
# Access database
from project.models import Base, Category, Product, User
from project.db import session
# Services
from project.services.categories import CategoryService
from project.services.config import ConfigService
from project.services.user import UserService

import random
import string
import httplib2
import json
import requests

# Authentification modules
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


auth = Blueprint('auth', __name__)


# Instantiate services
category_service = CategoryService()
config_service = ConfigService()
user_service = UserService()

# Get Client ID
CLIENT_ID = config_service.get_setting('client_id')

# Status Code Constansts
HTTP_STATUS_CODE_OK = 200
HTTP_STATUS_CODE_UNAUTHORIZED = 401
HTTP_STATUS_CODE_ERROR = 500

@auth.route('/login')
def showLogin():
    """App route function to display login page."""
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html',
                           STATE=state,
                           categories=category_service.get_all_categories(),
                           CLIENT_ID=CLIENT_ID)


@auth.route('/googleConnect', methods=['POST'])
def googleConnect():
    """Connect via Google Account and fetch User info."""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        make_json_response('Invalid state parameter.',
                            HTTP_STATUS_CODE_UNAUTHORIZED)
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        make_json_response('Invalid state parameter.',
                           HTTP_STATUS_CODE_UNAUTHORIZED)

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'
        .format(access_token))
    h = requests.get(url=url)
    result = json.loads(h.text)
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        make_json_response('error', HTTP_STATUS_CODE_ERROR)

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        make_json_response('Invalid state parameter.',
                           HTTP_STATUS_CODE_UNAUTHORIZED)

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        make_json_response('Invalid state parameter.',
                           HTTP_STATUS_CODE_UNAUTHORIZED)

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        make_json_response('Current user is already connected.',
                           HTTP_STATUS_CODE_OK)

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['email']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    result = "User is authorized!"
    flash("You are now logged in as {}".format(login_session['username']))
    return result


@auth.route('/googleDisconnect')
def googleDisconnect():
    """Disconnect user"""
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
    return redirect(url_for('categories.showCategories'))


# User Helper Functions
def make_json_response(data, status):
    """Makes http response, accepts message and status code"""
    response = make_response(data, status)
    response.headers['Content-Type'] = 'application/json'
    return response


def createUser(login_session):
    """Creates new login_session user, returns user.id."""
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = user_service.get_user_by_email(login_session['email'])
    return user.id


def getUserInfo(user_id):
    """Returns User object"""
    user = user_service.get_user_by_id(user_id)
    return user


def getUserID(email):
    """Returns user.id if exists, otherwise returns none."""
    try:
        user = user_service.get_user_by_email(email)
        return user.id
    except:
        return None
