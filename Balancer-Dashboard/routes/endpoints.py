import requests
import json

from socket import *
from flask import Blueprint, request, redirect

from app import build_error_response

endpoints = Blueprint('endpoints', __name__)


@endpoints.route('/register', methods=['POST'])
def register():
    """try:
        with open(HARDWARE_FILE, "r") as f:
            json_data = json.loads(f.read())
            hardware_id = json_data["hardware_id"]

    except:
        return build_error_response(400, "Error opening hardware file")

    try:
        with open(SOFTWARE_FILE, "r") as f:
            json_data = json.loads(f.read())
            software_id = json_data["software_id"]

    except:
        return build_error_response(400, "Error opening software file")

    data = dict(otc=request.form.get('otc'), hardware_id=hardware_id, software_id=software_id)
    response = requests.post(CONSUME_OTC_URL, data=data, timeout=TIMEOUT, verify=CA_CERTIFICATE)

    if response.status_code != 200:
        return response.text, 400

    client_socket = socket(AF_INET, SOCK_DGRAM)
    address = (CLIENT_APP_HOST, CLIENT_APP_PORT)

    client_socket.sendto(response.text.encode('utf-8'), address)

    return redirect("/")"""
    return ""


