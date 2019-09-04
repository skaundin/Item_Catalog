import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    items = relationship("Item", back_populates="category")

    def __repr__(self):
        return f"Category(name={self.name}, id={self.id})"


class Item(Base):
    __tablename__ = 'items'

    name = Column(String(80), nullable=False, unique=True)
    id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=True)
    user_id = Column(String(250), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Category, back_populates="items")

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,

        }

    def __repr__(self):
        return f"Item(name={self.name},\
                      id = {self.id}, \
                          description = {self.description}, \
                            category_id = {self.category_id})"


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
