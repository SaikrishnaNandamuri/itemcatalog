import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    email = Column(String(100), nullable=False)


class Costumes(Base):
    __tablename__ = "costumes"
    category_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    users = relationship(Users)


class Items(Base):
    __tablename__ = "items"
    item_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    wtype = Column(String(20), nullable=False)
    ctype = Column(String(20), nullable=False)
    gender = Column(String(20), nullable=False)
    price = Column(Integer, nullable=False)
    brand = Column(String(20), nullable=False)
    image_url = Column(String(500), nullable=False)
    category_id = Column(Integer, ForeignKey("costumes.category_id"))
    costumes = relationship(
        Costumes, backref=backref('items', cascade="all,delete-orphan"))

    @property
    def serialize(self):
        return {
               'name': self.name,
               'wtype': self.wtype,
               'price': self.price,
               'ctype': self.ctype,
               'image_url': self.image_url,
               'gender': self.gender,
               'brand': self.brand
           }


# end of the line
engine = create_engine("sqlite:///costumes.db")
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()
