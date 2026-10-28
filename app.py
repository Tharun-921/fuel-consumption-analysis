
import os
from pathlib import Path
from datetime import date

from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify
)
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

from models import db, User, FuelRecord

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__, instance_relative_config=True)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "dev-only-change-this-secret"
)

database_url = os.getenv("DATABASE_URL", "sqlite:///fuel_analysis.db")

if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql+psycopg://", 1
    )
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

csrf = CSRFProtect(app)
migrate = Migrate(app, db)


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    records = FuelRecord.query.order_by(FuelRecord.date.desc()).all()

    total_litres = sum(record.litres for record in records)
    total_cost = sum(record.total_cost for record in records)
    total_distance = sum(record.distance for record in records)

    average_mileage = (
        round(total_distance / total_litres, 2)
        if total_litres > 0 else 0
    )

    return render_template(
        "dashboard.html",
        records=records,
        total_litres=round(total_litres, 2),
        total_cost=round(total_cost, 2),
        total_distance=round(total_distance, 2),
        average_mileage=average_mileage,
        today=date.today().isoformat()
    )


@app.route("/fuel/add", methods=["POST"])
def add_fuel():
    try:
        vehicle_number = request.form["vehicle_number"].strip().upper()
        record_date = date.fromisoformat(request.form["date"])
        fuel_type = request.form["fuel_type"]
        litres = float(request.form["litres"])
        price = float(request.form["price_per_litre"])
        odometer = float(request.form["odometer"])
        distance = float(request.form["distance"])

        if not vehicle_number or litres <= 0 or price < 0:
            raise ValueError("Enter valid vehicle, fuel and price details.")

        if odometer < 0 or distance < 0:
            raise ValueError("Odometer and distance cannot be negative.")

        if fuel_type not in ("Petrol", "Diesel", "CNG", "Electric"):
            raise ValueError("Select a valid fuel type.")

        record = FuelRecord(
            vehicle_number=vehicle_number,
            date=record_date,
            fuel_type=fuel_type,
            litres=litres,
            price_per_litre=price,
            odometer=odometer,
            distance=distance
        )

        db.session.add(record)
        db.session.commit()
        flash("Fuel details saved successfully!", "success")

    except (ValueError, KeyError):
        db.session.rollback()
        flash("Invalid details. Please check all fields.", "error")
    except Exception:
        db.session.rollback()
        app.logger.exception("Could not save fuel record")
        flash("Could not save the record. Check your database setup.", "error")

    return redirect(url_for("dashboard"))


@app.route("/fuel/delete/<int:record_id>", methods=["POST"])
def delete_fuel(record_id):
    record = db.session.get(FuelRecord, record_id)

    if record is None:
        flash("Record not found.", "error")
    else:
        db.session.delete(record)
        db.session.commit()
        flash("Fuel record deleted.", "success")

    return redirect(url_for("dashboard"))


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "application": "Fuel Consumption Analysis System"
    })


@app.route("/login")
def login():
    return "Login functionality will be added next.", 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
