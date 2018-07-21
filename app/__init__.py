# Packages
from sys import argv
from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy

# Local
from config import Config

app = Flask(__name__, static_url_path="/static")
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = None
if len(argv) > 1:
    manager = Manager(app)
    manager.add_command("db", MigrateCommand)

from app import routes, models