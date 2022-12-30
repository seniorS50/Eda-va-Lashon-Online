from flask import Flask, render_template, request
from helpers import search_entries, get_text_HULTP
import json

app = Flask(__name__)

# Pre-load dictionary of files from JSON
with open('filenames.json') as f:
    data = json.load(f)
formatted_data = data
for datum in formatted_data:
    datum["ref"] = datum['book'] + " " + datum["ref"]

# Pre-load dictionary of city locations from JSON
with open('static/city_locs.json') as f:
    cities = json.load(f)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/api/search", methods = ['GET'])
def api():
    # If a generic query ("q") was requested, simply search and return all entries
    if 'q' in request.args:
        return json.dumps(search_entries(request.args["q"])['entries'])
    # If cities is the argument, then return the list of cities
    elif 'city' in request.args:
        return json.dumps(search_entries(request.args["city"])['cities'])
    else:
        return json.dumps({"error": "api request not recognized"})

@app.route("/api/all", methods = ['GET'])
def api_all():
    # Return the json file as a dict with "data" as the key and the rest of the file (the array) as the value
    return json.dumps({"data": formatted_data})

@app.route("/")
def index():
    return render_template("index.html", entry = data, cities = json.dumps(cities))

@app.route("/listen", methods = ['GET'])
def listen():
    # Read in the get request which has an HULTP number
    HULTP = int(request.args["HULTP"])
    text = get_text_HULTP(HULTP)
    # Get the recording that matches 
    entry = {}
    for datum in data:
        if str(datum["HULTP"]) == str(HULTP):
            entry = datum
            break
    return render_template("listen.html", entry=entry, text=text)

@app.route("/search", methods = ['GET'])
def search():
    results = search_entries(request.args["q"])
    if request.args:
        return render_template("index.html", entry = results['entries'], cities = json.dumps(results['cities']))
    else:
        return render_template("index.html", entry=[], cities = json.dumps(cities))