from project.models import Category, Product, User
from project.db import session


class ProductService():

    def __init__(self):
        self.session = session
        
    def get_product_by_id(self, product_id):
        """ return selected by its id product """
        return self.session.query(Product).filter_by(id=product_id).one()

    def get_latest_products(self, limit):
        """ returns the most recently added products"""
        return (self.session.query(Product)
                .order_by(Product.created_date.desc()).limit(limit))

    def get_all_products(self):
        """ return all products from catalog """
        return self.session.query(Product).all()

    def get_products_by_category_id(self, category_id):
        """ returns all products from selected category """
        return (self.session.query(Product)
                .filter_by(category_id=category_id).all())

    def products_count(self, category_id):
        """ returns count of how many products are in the category """
        return (self.session.query(Product)
                .filter_by(category_id=category_id).count())
