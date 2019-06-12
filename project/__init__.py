'''
Project 4 for Udacity Fullstack Nanodegree
Author: Aleksandr Zonis
'''

# Modules from Flask Library
from flask import Flask
import config

# Route modules
from categories.routes import categories
from products.routes import products
from jsonAPI.routes import jsonAPI
from auth.routes import auth

app = Flask(__name__)

# Configure the Application
app.config.from_object(config.DevelopmentConfig)

# Register Routes
app.register_blueprint(categories)
app.register_blueprint(products)
app.register_blueprint(jsonAPI)
app.register_blueprint(auth)
