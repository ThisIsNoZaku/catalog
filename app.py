from flask import Flask, render_template, request, jsonify, redirect, Response, session, make_response
import scripts.data as data
import base64
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError, verify_id_token
import httplib2
import random, string
import json
from scripts.data import Item, Category
app = Flask(__name__)

client_id = "711886336473-hsbqbk2952s7j499b2gok3brapm7ir1h.apps.googleusercontent.com"
verified_id_token = None

    
def unauthorized_response():
    return Response("The request authorization token was invalid", 401)


class authorizedOnly:
    __name__ = "authorisedOnly"
    
    def __init__(self, f):
        pass

    def __call__(self,f, *args):
        request_id = request.get_json().get("idToken")
        if request_id != verified_id_token:
            return unauthorized_response()
        else:
            return f(args)


@app.route("/")
def index():
    return render_template("index.html")
    
@app.route("/categories")
def categories():
    return jsonify({'categories':[
        {'description':c.description, 'id':c.category_id} for c in data.get_categories()
    ]})
    
@authorizedOnly
@app.route("/categories/create", methods=['POST'])
def categoryCreate():
    json = request.get_json()
    if not json.get('description'):
        return make_response("A category description wasn't included.", 400)
    category = Category(description=json.get("description"))
    data.create_category(category)
    return "OK"

@authorizedOnly    
@app.route("/categories/<int:category>/delete", methods=["DELETE"])
def delete_category(category):
    if not data.get_category(category):
        return make_response("There is no category with that id.", 404)
    data.delete_category(data.get_category(category))
    return "OK"

    
@authorizedOnly
@app.route("/categories/<int:category>/update", methods=["PUT"])
def update_category(category):
    if not data.get_category(category):
        return make_response("There is no category with that id.", 404)
    json = request.get_json().get("category")
    if not json:
        return make_response("The provided json was invalid.", 400)
    updated = data.get_category(json.get("id"))
    updated.description = json.get("description")
    data.update_category(updated)
    return "OK"


@app.route("/items")
@app.route("/categories/<int:category>/items")
def get_items(category=None):
    items = None
    if category:
        retrieved = data.get_category(category)
        if not retrieved:
            return make_response("There is no category with that id.", 404)
        items = retrieved.items
    else:
        items = data.get_items()
    transformed = [{'id' : i.item_id, 'name' : i.name, 'description' : i.description} for i in items]
    json = jsonify({
        'items' : transformed
    })
    return json
    

@app.route("/items/<int:item>")
def get_item(item):
    retrieved = data.get_item(item)
    if not retrieved:
        return make_response("There is no item with that id.", 404)
    return jsonify({"item": retrieved})
    
    
@authorizedOnly
@app.route("/items/create", methods=["POST"])
def create_item():
    item_json = request.get_json().get("item")
    missing_fields = []
    if not item_json.get("name"):
        missing_fields.append('name')
    if not item_json.get("description"):
        missing_fields.append('description')
    if missing_fields:
        return make_response("Payload was missing required fields: %s" % missing_fields.join(','), 400)
    new_item = Item(name=item_json.get("name"), description=item_json.get("description"))
    data.create_item(new_item)
    return "OK"


@authorizedOnly 
@app.route("/items/<int:item>/update", methods=["PUT"])
def update_item(item):
    item_json = request.get_json().get("item")
    if not item_json:
        return make_response("Json payload must contain object property named 'item'", 422)
    existing_item = data.get_item(item)
    if not existing_item:
        return make_response("There is no item with that id", 404)
    if item_json.get("name"):
        existing_item.name = item_json.get('name')
    if item_json.get("description"):
        existing_item.description = item_json.get('description')
    result = data.update_item(existing_item)
    return jsonify(result)


@authorizedOnly 
@app.route("/items/<int:item>/delete", methods=["DELETE"])
def delete_item(item):
    existing_item = data.get_item(item)
    if not existing_item:
        return make_response("There is no item with that id", 404)
    data.delete_item(item)
    return "OK"
    

@app.route("/login", methods=["POST"])
def login():
    token = request.get_json().get("idToken")
    http = httplib2.Http('cache')
    response, content = http.request("https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=%s" % token)
    content = json.loads(content.decode())
    if response.status is not 200:
        return make_response("Failed to upgrade the authorization code.", 401)
    if content['aud'] != client_id:
        return make_response("Aud was not for this client.", 401)
    verified_id_token = token
    return "OK"


@app.before_request
def login_state():
    session['state'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))

    
app.secret_key = "Not a real secret, but not a real website either."

if (__name__ == "__main__"):
    app.run()