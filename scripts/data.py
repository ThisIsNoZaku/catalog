from sqlalchemy import (create_engine, Column, Integer, String,
                        ForeignKey, Table)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import inspect

# Taken from tutorial @ http://zetcode.com/db/sqlalchemy/
eng = create_engine("postgresql://server@localhost/item_catalog")
connection = eng.connect()
Session = sessionmaker(bind=eng)()


Base = declarative_base()


# Named-only parameters implementation
# from http://stackoverflow.com/a/33794199/5602822
class Item(Base):
    __tablename__ = "items"
    item_id = Column(Integer, primary_key=True)
    name = Column("name", String)
    description = Column("description", String)

    def __init__(self, **kwargs):
        for arg in ["name", "description", "category"]:
            value = kwargs.pop(arg, None)
            if not value:
                raise TypeError("Parameter named wasn't set." % arg)
            setattr(self, arg, value)

        setattr(self, "id", kwargs.pop("id", None))


class Category(Base):
    __tablename__ = "categories"
    category_id = Column("category_id", Integer, primary_key=True)
    description = Column("description", String)
    join_table = Table("item_categories",
                       Base.metadata,
                       Column("item_id",
                              Integer,
                              ForeignKey("items.item_id")),
                       Column("category_id",
                              Integer,
                              ForeignKey("categories.category_id")))
    items = relationship(Item,
                         secondary=join_table)

    def __init__(self, **kwargs):
        for arg in ["description"]:
            value = kwargs.pop(arg, None)
            if not value:
                raise TypeError("Parameter named wasn't set." % arg)
            setattr(self, arg, value)

        setattr(self, "id", kwargs.pop("id", None))


# Type checking decorator adapted from
# http://stackoverflow.com/a/15300191/5602822
def accepts(*types):
    def check_accepts(f):
        assert len(types) == len(inspect.getargspec(f).args)

        def new_f(*args, **kwds):
            for (a, t) in zip(args, types):
                assert isinstance(a, t), \
                       "arg %r does not match %s" % (a, t)
            return f(*args, **kwds)
        new_f.__name__ = f.__name__
        return new_f
    return check_accepts


def get_category(id):
    return Session.query(Category).filter(Category.category_id == id).first()


def get_categories():
    """
    Returns a list of tuples containing the ids and descriptions
    of all categories.
    """
    return Session.query(Category).all()


@accepts(Category)
def create_category(category):
    """
    Creates a new category with the given string
    description
    """
    Session.add(category)
    Session.commit()


@accepts(Category)
def delete_category(category):
    """
    Deletes the category with the given id.
    """
    Session.delete(category)
    Session.commit()


@accepts(Category)
def update_category(category):
    """
    Takes a tuple containing an 'id' entry and optionally a
    'description' entry.

    The category with the given id has its description
    updated with the given values.
    """

    Session.add(category)
    Session.commit()


def get_items():
    """
    Returns a list of tuples of all items.
    """
    return Session.query(Item).all()


@accepts(Item)
def create_item(item):
    """
    Save the given new item in the database.
    """
    Session.add(item)
    Session.commit()


@accepts(Item)
def delete_item(item):
    """
    Delete the item with the given id.
    """
    Session.delete(item)
    Session.commit()


@accepts(Item)
def update_item(item):
    """
    Persists the given Item instance.

    """
    Session.add(item)
    Session.commit()
