from project.models import Category, Product, User
from project.db import session

class UserService():

	def __init__(self):
		self.session = session

	def get_user_by_email(self, email):
		"""Returns User object by email"""
		return self.session.query(User).filter_by(email=email).one()

	def get_user_by_id(self, user_id):
		"""Returns User object by id"""
		return self.session.query(User).filter_by(id=user_id).one()