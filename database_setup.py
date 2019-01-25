from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
 
Base = declarative_base()


class User(Base):
  __tablename__= 'user'

  id = Column(Integer, primary_key = True)
  name = Column(String(500), nullable = False)
  email = Column(String(500), nullable = False)


class Category(Base):
    __tablename__ = 'category'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
       }


class Product(Base):
    __tablename__ = 'product'


    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    image_url = Column(String(250))
    product_url = Column(String(250))
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category, backref=backref("items", cascade="all,delete"))
    
    
    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'description'         : self.description,
           'id'         : self.id,
           'image_url'         : self.image_url,
           'product_url'         : self.product_url,
           'category_id'         : self.category_id
       }



engine = create_engine('sqlite:///furniturecatalog.db')
 

Base.metadata.create_all(engine)
