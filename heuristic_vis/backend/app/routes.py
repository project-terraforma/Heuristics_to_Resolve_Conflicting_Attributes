from flask import Blueprint, jsonify

main = Blueprint('main', __name__)

@main.route("/api/hello")
def hello():
    return jsonify({"message": "Hello from Flask!"})
