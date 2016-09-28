from flask import Flask, render_template, request, jsonify, redirect, Response, session, make_response
import scripts.data as data
import base64
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError, verify_id_token
import httplib2
import random, string
import json
app = Flask(__name__)

client_id = "711886336473-hsbqbk2952s7j499b2gok3brapm7ir1h.apps.googleusercontent.com"
verified_id_token = None

@app.route("/")
def index():
	return render_template("index.html")
	
@app.route("/categories")
def categories():
	error = None
	return jsonify({'categories':data.get_categories()})
	
@app.route("/categories/create", methods=['POST'])
def categoryCreate():
	data.create_category(json.get('category'))
	return "OK"
	
@app.route("/categories/<int:category>/delete", methods=["DELETE"])
def delete_category(category):
	if not authorize():
		return unauthorized_response()
	data.delete_category(category)
	return "OK"
	
@app.route("/categories/<int:category>/update", methods=["PUT"])
def update_category(category):
	if not authorize():
		return unauthorized_response()
	json = request.get_json()
	category_props = {}
	category_props["id"] = json.get("category").get("id")
	category_props["description"] = json.get("category").get("description")
	data.update_category(category_props)
	return "OK"

	
@app.route("/items")
@app.route("/categories/<int:category>/items")
def items(category=None):
	error = None
	if(category):
		return jsonify({'items' :data.get_items_for_category(category)})
	else:
		return jsonify({'items' : data.get_items()})

@app.route("/items/<int:item>")
def item(item):
	return jsonify({"item": data.get_item_by_name(item)})
	
	
@app.route("/items/create", methods=["POST"])
def create_item():
	if not authorize():
		return unauthorized_response()
	json = request.get_json()
	item_json = json.get("item")
	item_props = {}
	item_props['name'] = item_json.get("name")
	item_props['description'] = item_json.get("description")
	item_props['category'] = item_json.get("category")
	data.create_item(item_props)
	return "OK"

@app.route("/items/<int:item>/update", methods=["PUT"])
def update_item(item):
	if not authorize():
		return unauthorized_response()
	json = request.get_json()
	item_json = json.get("item")
	item_props = {}
	item_props['name'] = item_json.get("name")
	item_props['description'] = item_json.get("description")
	item_props['category'] = item_json.get("category")
	item_props['id'] = item_json.get("id")
	print(item_props)
	result = data.update_item(item_props)
	print(result)
	return jsonify(result)

@app.route("/items/<int:item>/delete", methods=["DELETE"])
def delete_item(item):
	if not authorize():
		return unauthorized_response()
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



def authorize():
	request_id = request.get_json().get("idToken")
	return request_id == verified_id_token
	
def unauthorized_response():
	return Response("The request authorization token was invalid", 401)


@app.before_request
def login_state():
	session['state'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))

	
app.secret_key = "Not a real secret, but not a real website either."

if (__name__ == "__main__"):
	app.run()