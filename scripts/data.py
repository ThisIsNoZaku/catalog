from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

eng = create_engine("postgresql://server@localhost/item_catalog")
connection = eng.connect()
Session = sessionmaker(bing=eng)()

def get_categories():
    """
    Returns a list of tuples containing the ids and descriptions
    of all categories.
    """
	
	return Session.query(Category).all()


def get_items_for_category(category):
    """
    Returns a list of tuples of all items whose category
    is the given category id.
    """
    result = []
    try:
        cursor = connection.cursor()
        cursor.execute("""select * from items
        inner join
        item_categories on items.item_id = item_categories.item_id
        inner join
        categories on categories.category_id = item_categories.category_id
        and categories.category_id = %s
        """, (category,))

        result = cursor.fetchall()
    except:
        connection.rollback()
    finally:
        cursor.close()
    return result


def get_items():
    """
    Returns a list of tuples of all items.
    """
    result = None
    try:
        cursor = connection.cursor()
        cursor.execute("select * from items")
        result = cursor.fetchall()
    except:
        connection.rollback()
    finally:
        cursor.close()
    return result


def create_item(item):
    """
    Create a new item, using the given tuple of properties.
    The tuple must contain an entry for 'name', 'description' and 'category'.
    """
    try:
        cursor = connection.cursor()
        cursor.execute(
            """with new_id as
            (insert into items(name, description)
            values(%s, %s) returning item_id)
            insert into item_categories(item_id, category_id)
            values ((select item_id from new_id), %s)""",
            (item['name'], item['description'], item['category'])
        )
        connection.commit()
        return cursor.rowcount != 0
    except Exception as ex:
        connection.rollback()
        raise ex
    finally:
        cursor.close()


def delete_item(item):
    """
    Delete the item with the given id.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("delete from items where items.item_id = %s", (item,))
        connection.commit()
    except Exception as ex:
        connection.rollback()
        raise ex
    finally:
        cursor.close()


def update_item(item):
    """
    Takes a tuple containing an 'id' entry and optionally a
    'description' and/or 'name' entry.

    The item with the given id has its name and/or description
    updated with the given values.
    """
    try:
        cursor = connection.cursor()
        if(item["description"]):
            cursor.execute("""update items
                              set description = %s
                              where item_id = %s""",
                           (item["description"], item["id"],))
        if(item["name"]):
            cursor.execute("""update items set name = %s
                              where item_id = %s""",
                           (item["name"], item["id"],))
        connection.commit()
        cursor.execute("select * from items where item_id = %s", (item["id"],))
        return cursor.fetchall()
    except Exception as ex:
        connection.rollback()
        raise ex
    finally:
        cursor.close()


def create_category(category):
    """
    Creates a new category with the given string
    description
    """
    try:
        cursor = connection.cursor()
        cursor.execute("insert into categories(description) values(%s)",
                       (category,))
        connection.commit()
    except Exception as ex:
        connection.rollback()
        raise ex
    finally:
        cursor.close()


def delete_category(category):
    """
    Deletes the category with the given id.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""delete from categories
                          where categories.category_id = %s""",
                       (category,))
        connection.commit()
    except Exception as ex:
        connection.rollback()
        raise ex
    finally:
        cursor.close()


def update_category(category):
    """
    Takes a tuple containing an 'id' entry and optionally a
    'description' entry.

    The category with the given id has its description
    updated with the given values.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""update categories
                          set description = %s where category_id = %s""",
                       (category["description"], category["id"],))
        connection.commit()
        print("Update complete")
    except Exception as ex:
        connection.rollback()
        raise ex
    finally:
        cursor.close()


Base = declarative_base()
		
class Item(Base):

	def __init__(self, **kwargs):
		for arg in ["name", "description"]
			value = kwargs.pop(arg, None)
			if not value:
				raise TypeError("Parameter named wasn't set." % arg)
			setattr(self, arg, value)

		setattr(self, "id", kwargs.pop("id", None))

class Category(Base):

	def __init__(self, **kwargs):
		for arg in ["description"]
			value = kwargs.pop(arg, None)
			if not value:
				raise TypeError("Parameter named wasn't set." % arg)
			setattr(self, arg, value)

		setattr(self, "id", kwargs.pop("id", None))