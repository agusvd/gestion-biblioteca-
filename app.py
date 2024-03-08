from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# config inicial
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'clavesecreta'
# no cache
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

SQLAlchemy(app)
