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
from models import Base, Category, Product, User

import random
import string
import httplib2
import json
import requests
import config



# Authentification modules
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


app = Flask(__name__)

# Configure the Application 

app.config.from_object(config.DevelopmentConfig)

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



from categories.routes import categories
from products.routes import products
from jsonAPI.routes import jsonAPI
from auth.routes import auth
app.register_blueprint(categories)
app.register_blueprint(products)
app.register_blueprint(jsonAPI)
app.register_blueprint(auth)


