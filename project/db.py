from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base


class DBConnector():

    engine = create_engine('sqlite:///furniturecatalog.db',
                           connect_args={'check_same_thread': False})
    Base.metadata.bind = engine

    def __init__(self):
        self.DBSession = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.DBSession()

# Connect to the database and create session
session = DBConnector().get_session()