# Item Catalog
This application is an online item catalog. Users can log in via their Google account and may add, change and remove items and categories.

It is a single page application, communicating via ajax with the server.

### Installation
This app uses postgresql as the database. 

Open a terminal or command prompt in the project root directory. Connect to your postgresql instance and execute the command "\i database.sql". This will create the necessary tables and populate them with some pregenereted data.

After setting up the database, the server can also be started via terminal/command line in the same directory.

Use the command "export FLASK_APP=app.py" on linux or "set FLASK_APP=app.py" on windows then "flask run" to start the server. The app is then accessible at "localhost:5000" in the browser.