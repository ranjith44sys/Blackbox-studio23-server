from flask import Blueprint, request, jsonify
from database.mongo_connection import db

photo_routes = Blueprint("photo_routes", __name__)

@photo_routes.route("/upload", methods=["POST"])
def upload_photo():
    data = request.json
    db.photos.insert_one(data)
    return jsonify({"message": "Photo uploaded successfully"})
