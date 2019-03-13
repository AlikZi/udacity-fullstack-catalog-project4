from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base


class DBConnector():

	engine = create_engine('sqlite:///furniturecatalog.db')
	Base.metadata.bind = engine
	
	def __init__(self):
		self.DBSession = sessionmaker(bind=self.engine)
		

	def get_session(self):
		return self.DBSession()