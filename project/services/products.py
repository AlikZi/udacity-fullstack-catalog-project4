from project.models import Category, Product, User
from project.db import DBConnector


class ProductService():

    def __init__(self):
        self.session = DBConnector().get_session()

    def get_product_by_id(self, prod_id):
        """ return selected by its id product """
        return self.session.query(Product).filter_by(id=prod_id).one()

    def get_latest_products(self, limit):
        """ returns the most recently added products"""
        return (self.session.query(Product)
                .order_by(Product.created_date.desc()).limit(limit))

    def get_all_products(self):
        """ return all products from catalog """
        return self.session.query(Product).all()

    def get_products_by_cat_id(self, cat_id):
        """ returns all products from selected category """
        return (self.session.query(Product)
                .filter_by(category_id=cat_id).all())

    def products_count(self, cat_id):
        """ returns count of how many products are in the category """
        return (self.session.query(Product)
                .filter_by(category_id=cat_id).count())
