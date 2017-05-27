import json
import logging

from flask import Flask, Response
from flask_script import Manager, Server
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__, static_url_path='/static')

app.config.from_pyfile('settings.py')

logger = logging.getLogger('werkzeug')
handler = logging.FileHandler(app.config["LOG_FILE"])
logger.addHandler(handler)
app.logger.addHandler(handler)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "gui.login"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command("runserver", Server(host=app.config["HOSTS_ALLOW"], port=app.config["PORT"]))


@manager.command
def load_data():
    import loaddata
    loaddata.populate()


from models.user import User


@login_manager.user_loader
def load_user(id):
    try:
        return User.query.get(id)
    except:
        return None

# Method used to unify responses sintax
def build_response(status_code, description="", error="", data=""):
    jd = {"status_code" : status_code, "error": error, "description": description, "data": data}
    resp = Response(response=json.dumps(jd), status=status_code, mimetype="application/json")
    return resp


def build_error_response(status, error_title, error_desc):
    jd = {"status_code:": status, "error": error_title, "description": error_desc, "data": ""}
    resp = Response(response=json.dumps(jd), status=status, mimetype="application/json")
    return resp


from routes.endpoints import endpoints
from routes.gui import gui

app.register_blueprint(gui)
app.register_blueprint(endpoints, url_prefix='/endpoints')
