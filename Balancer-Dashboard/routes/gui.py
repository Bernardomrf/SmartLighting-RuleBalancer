import json
import logging

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required
import requests
from app import build_response, build_error_response, db
from models.user import User
from models.gateway import Device, Rule, Gateway

gui = Blueprint('gui', __name__, template_folder='templates')
logger = logging.getLogger()

@gui.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('gui.gateways'))

    return redirect(url_for('gui.login'))


@gui.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    if user.verify_password(request.form['password']):
        login_user(user)

        return redirect(url_for('gui.gateways'))

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


@gui.route('/gateways')
@login_required
def gateways():
    #logger.error("Gateway")
    gateways = get_gateways()
    data = {"gateways": gateways}
    return render_template('gateways.html', **data)

@gui.route('/rules')
@login_required
def rules():
    #logger.error("Rule")
    rules = get_rules()
    data = {"rules": rules}
    return render_template('rules.html', **data)

@gui.route('/devices')
@login_required
def devices():
    #logger.error("Gateway")
    devices = get_devices()
    data = {"devices": devices}
    return render_template('devices.html', **data)


def get_gateways():
    gateways = Gateway.query.order_by(Gateway.id).all()
    data = []
    for gateway in gateways:
        data.append(gateway.serialize)
    return data

def get_rules():
    rules = Rule.query.order_by(Rule.r_id).all()
    data = []
    for rule in rules:
        data.append(rule.serialize)
    return data

def get_devices():
    devices = Device.query.order_by(Device.name).all()
    data = []
    for device in devices:
        data.append(device.serialize)
    return data
