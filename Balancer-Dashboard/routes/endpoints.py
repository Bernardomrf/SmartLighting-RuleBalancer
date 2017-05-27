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
