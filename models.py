
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)


class FuelRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(30), nullable=False)
    date = db.Column(db.Date, nullable=False)
    fuel_type = db.Column(db.String(30), nullable=False)
    litres = db.Column(db.Float, nullable=False)
    price_per_litre = db.Column(db.Float, nullable=False)
    odometer = db.Column(db.Float, nullable=False)
    distance = db.Column(db.Float, nullable=False)

    @property
    def total_cost(self):
        return round(self.litres * self.price_per_litre, 2)

    @property
    def mileage(self):
        if self.litres > 0:
            return round(self.distance / self.litres, 2)
        return 0
