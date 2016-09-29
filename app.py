from flask import (Flask, render_template, request, jsonify,
                   redirect, Response, session, make_response)
import scripts.data as data
import base64
from oauth2client.client import (flow_from_clientsecrets,
                                 FlowExchangeError,
                                 verify_id_token)
import httplib2
import random
import string
import json
from scripts.data import Item, Category
app = Flask(__name__)

client_id = ("711886336473-hsbqbk2952s7j499b2gok3brapm7ir1h."
             "apps.googleusercontent.com")
verified_id_token = None


def unauthorized_response():
    return make_response("The request authorization token was invalid", 401)


def authenticatedOnly(f, *args):
    """
    Decorator for methods that are only available to authenticated
    clients.
    """
    def new_f(*args):
        request_id = request.get_json().get("idToken")
        if request_id != verified_id_token:
            return unauthorized_response()
        else:
            return f(args)
    return new_f


def usesCategory(f):
    """
    Decorator for handler methods that require a category instance.
    """
    def new_f(category_id):
        category = data.get_category(category_id)
        if not category:
            return make_response("There is no category with that id.", 404)
        return f(category)
    new_f.__name__ = f.__name__
    return new_f


def usesItem(f):
    """
    Decorator for handler methods that require a category instance.
    """
    def new_f(item_id):
        item = data.get_item(item_id)
        if not item:
            return make_response("There is no item with that id.", 404)
        print()
        return f(item)
    new_f.__name__ = f.__name__
    return new_f


def jsonPayload(f):
    """
    Decorator for handler methods that accept only json payload.
    """
    def new_f(*args):
        print("Detecting json")
        if not request.is_json():
            return make_response("The endpoint requires a json request body.", 400)
        return f(*args)
    new_f.__name__ = f.__name__
    return new_f


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/categories.json")
def categories():
    """
    JSON endpoint for all item categories.
    """
    return jsonify({'categories': [
        {'description': c.description,
         'id': c.category_id} for c in data.get_categories()
    ]})


@authenticatedOnly
@app.route("/categories/create", methods=['POST'])
@jsonPayload
def categoryCreate():
    """
    Endpoint for creating a new item category, takes a json payload
    with a 'category' property and populates a Category instance with
    it.
    """
    json = request.get_json().get("category")
    if not json.get('description'):
        return make_response("Json payload requires a 'category'"
                             " object with a 'description' property.", 400)
    category = Category(description=json.get("description"))
    data.create_category(category)
    return "OK"


@authenticatedOnly
@app.route("/categories/<int:category_id>/delete", methods=["DELETE"])
@usesCategory
def delete_category(category):
    """
    Endpoint to delete a category.
    """
    data.delete_category(category)
    return "OK"


@authenticatedOnly
@jsonPayload
@app.route("/categories/<int:category_id>/update", methods=["PUT"])
@usesCategory
def update_category(category):
    """
    Endpoint to update a category, takes a json payload and updates the
    category with the specified id with the payload.
    """
    json = request.get_json().get("category")
    if not json:
        return make_response("The json payload requires a 'category' property.", 
                             400)
    category.description = json.get("description")
    data.update_category(category)
    return "OK"


@app.route("/items.json")
def get_items():
    """
    JSON endpoint to get all items.
    """
    return jsonify({
        'items': [{'id': i.item_id,
                    'name': i.name,
                    'description': i.description}
                   for i in data.get_items()]
    })


@app.route("/categories/<int:category_id>/items.json")
@usesCategory
def get_items_for_category(category):
    """
    JSON endpoint to get all items for the specified category.
    """
    return jsonify({
        'items': [{'id': i.item_id,
                    'name': i.name,
                    'description': i.description}
                   for i 
                   in category.items]
    })

@app.route("/items/<int:item_id>.json")
@usesItem
def get_item(item):
    """
    JSON endpoint for a single item.
    """
    return jsonify({
        'item': {'id': item.item_id,
                 'name': item.name,
                 'description': item.description}
    })


@authenticatedOnly
@app.route("/items/create", methods=["POST"])
@jsonPayload
def create_item():
    """
    Endpoint to create a new item, takes a json payload and
    creates a new instance from it.
    """
    item_json = request.get_json().get("item")
    if not item_json:
        return make_response("Json payload requires a 'item' property", 400)
    missing_fields = []
    if not item_json.get("name"):
        missing_fields.append('name')
    if not item_json.get("description"):
        missing_fields.append('description')
    if missing_fields:
        return make_response("Payload was missing required fields: %s" %
                             missing_fields.join(','), 400)
    new_item = Item(name=item_json.get("name"),
                    description=item_json.get("description"))
    # If a category is specified, add to it and persist
    if item_json.get("category"):
        item_category = data.get_category(item_json.get("category"))
        item_category.items.append(new_item)
        data.update_category(item_category)
    data.create_item(new_item)
    return "OK"


@authenticatedOnly
@app.route("/items/<int:item_id>/update", methods=["PUT"])
def update_item(item):
    """
    Endpoint to update an item, takes a json payload and updates
    the existing instance with its information.
    """
    item_json = request.get_json().get("item")
    if not item_json:
        return make_response("Json payload must contain"
                             " object property named 'item'",
                             422)
    existing_item = data.get_item(item)
    if not existing_item:
        return make_response("There is no item with that id", 404)
    if item_json.get("name"):
        existing_item.name = item_json.get('name')
    if item_json.get("description"):
        existing_item.description = item_json.get('description')
    result = data.update_item(existing_item)
    return jsonify(result)


@authenticatedOnly
@app.route("/items/<int:item_id>/delete", methods=["DELETE"])
@usesItem
def delete_item(item):
    """
    End point to delete an item.
    """
    data.delete_item(item)
    return "OK"


@app.route("/login", methods=["POST"])
def login():
    """
    Validates Google login provided by the client.
    """
    token = request.get_json().get("idToken")
    http = httplib2.Http('cache')
    response, content = http.request("https://www.googleapis.com/oauth2/v3/"
                                     "tokeninfo?id_token=%s"
                                     % token)
    content = json.loads(content.decode())
    if response.status is not 200:
        return make_response("Failed to upgrade the authorization code.", 401)
    if content['aud'] != client_id:
        return make_response("Aud was not for this client.", 401)
    verified_id_token = token
    return "OK"


@app.before_request
def login_state():
    """
    State token to prevent session highjacking.
    """
    if session['state'] and request.headers.get('session'):
        return make_response("Invalid session state", 401)
    session['state'] = (
        ''.join(random.choice(string.ascii_uppercase +
                              string.digits)
                for x in range(32))
    )


app.secret_key = "Not a real secret, but not a real website either."

if (__name__ == "__main__"):
    app.run(host='0.0.0.0', port=5000)
