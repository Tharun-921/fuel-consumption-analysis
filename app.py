
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template, jsonify
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

from models import db, User

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
login_manager.login_message_category = "info"

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


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "application": "Fuel Consumption Analysis System"
    })


@app.route("/login")
def login():
    return "Login page will be implemented in the next step.", 200


@app.route("/dashboard")
def dashboard():
    return "Dashboard will be implemented in a later step.", 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
