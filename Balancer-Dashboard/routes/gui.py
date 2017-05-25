import json

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required

from app import db
from models.user import User
from models.gateway import Device, Rule, Gateway

gui = Blueprint('gui', __name__, template_folder='templates')


@gui.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('gui.settings'))

    return redirect(url_for('gui.login'))


@gui.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    if user.verify_password(request.form['password']):
        login_user(user)

        return redirect(url_for('gui.settings'))

    return 'Bad login'


@gui.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('gui.login'))


@gui.route('/change_password', methods=['POST'])
@login_required
def change_password():
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if new_password != confirm_password:
        return redirect(url_for("gui.settings", pass_change=True, success=False))

    user = User.query.filter_by(username=current_user.username).first()

    user.update_password(new_password)

    db.session.commit()

    return redirect(url_for("gui.settings", pass_change=True, success=True))


@gui.route('/settings')
@login_required
def settings():
    pass_change = request.args.get("pass_change")
    success = request.args.get("success")

    try:
        pass_change = eval(pass_change)
        success = eval(success)
    except Exception:
        pass_change = False
        success = False

    return render_template('settings.html', pass_change=pass_change, success=success)


"""@gui.route('/about')
@login_required
def about():
    args = {}
    try:
        f = open(DEVICE_FILE, "r")
        data = json.loads(f.read())
        f.close()

        f = open(HASS_VERSION_FILE, "r")
        args["hass_version"] = f.read()
        f.close()

        args["gw_id"] = data["random_id"]
        args["gw_hw_id"] = data["hardware"]["random_id"]
        args["gw_user_id"] = data["user"]

        args["gw_gui_version"] = VERSION
        args["gw_client_version"] = data["software"]["version"]

        f = open(CONFIG_FILE, "r")
        yaml_file = yaml.load(f.read())
        f.close()
        args["gw_plug_ins"] = yaml_file["components"]

    except:
        pass
    return render_template('about.html', **args)
"""
@gui.route('/register')
@login_required
def register():
    return render_template('register.html')
