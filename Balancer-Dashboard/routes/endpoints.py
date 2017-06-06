import requests
import json
from app import logger

from socket import *
from flask import Blueprint, request, redirect
from models.gateway import Gateway, Device, Rule
from app import build_response, build_error_response, db

endpoints = Blueprint('endpoints', __name__)

@endpoints.route('/gateway', methods=['POST'])
def gateway():
    try:
        if 'hostname' not in request.form or 'status' not in request.form or 'last_hb' not in request.form:
            return build_error_response(400, "Missing post arguments")

        hostname = request.form['hostname']
        last_hb = request.form['last_hb']
        status = request.form['status']

        gateway = Gateway.query.filter_by(hostname=hostname).first()
        if gateway is not None:
            #UPDATE
            gateway.status = status
            gateway.last_heartbeat = last_hb
            db.session.commit()

            return build_response(200, data=gateway.serialize)

        gateway = Gateway(hostname=hostname, status=status, last_heartbeat=last_hb)
        db.session.add(gateway)
        db.session.commit()
    except Exception as e:

        db.session.rollback()
        return build_error_response(400, "ERROR", e)

    return build_response(200, data=gateway.serialize)


@endpoints.route('/rule', methods=['POST'])
def rule():
    try:
        if 'id' not in request.form:
            return build_error_response(400, "Missing post arguments","")

        if 'rule' in request.form:

            gateway_id = None
            r_id = request.form['id']
            json_rule = request.form['rule']

            rule = Rule.query.filter_by(r_id=r_id).first()

            if rule is not None:
                #UPDATE
                rule.json_rule = json_rule
                rule.gateway_id = gateway_id
                db.session.commit()

                return build_response(200, data=rule.serialize)

            rule = Rule(r_id=r_id, gateway_id=gateway_id, json_rule=json_rule)
            db.session.add(rule)
            db.session.commit()

        if 'hostname' in request.form:
            hostname = request.form['hostname']
            r_id = request.form['id']
            gateway = Gateway.query.filter_by(hostname=hostname).first()
            gateway_id = gateway.id

            rule = Rule.query.filter_by(r_id=r_id).first()
            if rule is None:
                return build_error_response(400, "Missing post arguments","")

            rule.gateway_id = gateway_id
            db.session.commit()

    except Exception as e:

        db.session.rollback()
        return build_error_response(400, "ERROR", e)

    return build_response(200, data=rule.serialize)

@endpoints.route('/device', methods=['POST'])
def device():
    try:
        if 'name' not in request.form or 'gateway' not in request.form:
            return build_error_response(400, "Missing post arguments","")

        device_name = request.form['name']
        hostname = request.form['gateway']
        gateway = Gateway.query.filter_by(hostname=hostname).first()
        gateway_id = gateway.id

        device = Device.query.filter_by(name=device_name).first()
        if device is not None:
            device.gateway_id = gateway_id
            db.session.commit()
            return build_response(200, data=device.serialize)

        device = Device(name=device_name, gateway_id=gateway_id)
        db.session.add(device)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return build_error_response(400, "ERROR", e)

    return build_response(200, data=device.serialize)
