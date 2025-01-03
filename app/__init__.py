from datetime import timedelta
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

app = Flask(__name__)

CORS(app)

app.config["SECRET_KEY"] = "uwenndknsksdieewo"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

client = MongoClient("localhost", 27017)

db = client.hrportal


from .shifts.routes import shifts
from .report.routes import report
from .authentication.routes import auth

app.register_blueprint(shifts, url_prefix="/shifts")
app.register_blueprint(report, url_prefix="/report")
app.register_blueprint(auth, url_prefix="/auth")