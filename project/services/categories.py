from project.models import Category, Product, User
from project.db import DBConnector


class CategoryService():

    def __init__(self):
        self.session = DBConnector().get_session()

    def get_all_categories(self):
        """ returns all categories ordered by name"""
        return self.session.query(Category).order_by(Category.name).all()

    def get_category_by_id(self, category_id):
        """ returns a category that is selected to be it's id """
        return self.session.query(Category).filter_by(id=category_id).one()
