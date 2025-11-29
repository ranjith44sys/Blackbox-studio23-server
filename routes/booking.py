from flask import Blueprint, request, jsonify
from database.mongo_connection import db

booking_routes = Blueprint("booking_routes", __name__)

@booking_routes.route("/create", methods=["POST"])
def create_booking():
    data = request.json
    db.bookings.insert_one(data)
    return jsonify({"message": "Booking saved successfully!"})
