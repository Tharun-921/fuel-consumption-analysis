
from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def utc_now():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)

    vehicles = db.relationship(
        "Vehicle", back_populates="user", cascade="all, delete-orphan"
    )


class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    registration_number = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), default="")
    vehicle_type = db.Column(db.String(30), nullable=False)
    fuel_type = db.Column(db.String(20), nullable=False)
    manufacturing_year = db.Column(db.Integer)
    odometer_reading = db.Column(db.Float, nullable=False, default=0)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)

    user = db.relationship("User", back_populates="vehicles")
    fuel_records = db.relationship(
        "FuelRecord", back_populates="vehicle", cascade="all, delete-orphan"
    )
    expenses = db.relationship(
        "VehicleExpense", back_populates="vehicle", cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "registration_number",
            name="uq_vehicle_user_registration"
        ),
    )


class FuelRecord(db.Model):
    __tablename__ = "fuel_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    vehicle_id = db.Column(
        db.Integer, db.ForeignKey("vehicles.id"), nullable=False, index=True
    )
    date = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    odometer_reading = db.Column(db.Float, nullable=False)
    distance_km = db.Column(db.Float, nullable=False, default=0)
    fuel_litres = db.Column(db.Float, nullable=False)
    price_per_litre = db.Column(db.Float, nullable=False)
    fuel_station = db.Column(db.String(150), default="")
    payment_method = db.Column(db.String(30), default="Other")
    full_tank = db.Column(db.Boolean, nullable=False, default=False)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)

    vehicle = db.relationship("Vehicle", back_populates="fuel_records")

    @property
    def total_cost(self):
        return round(self.fuel_litres * self.price_per_litre, 2)

    @property
    def mileage(self):
        if self.distance_km > 0 and self.fuel_litres > 0:
            return round(self.distance_km / self.fuel_litres, 2)
        return None


class VehicleExpense(db.Model):
    __tablename__ = "vehicle_expenses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    vehicle_id = db.Column(
        db.Integer, db.ForeignKey("vehicles.id"), nullable=False, index=True
    )
    date = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    category = db.Column(db.String(40), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(300), default="")
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)

    vehicle = db.relationship("Vehicle", back_populates="expenses")


def set_user_password(user, password):
    user.password_hash = generate_password_hash(password)


def check_user_password(user, password):
    return check_password_hash(user.password_hash, password)
