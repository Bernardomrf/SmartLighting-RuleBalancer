from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
from app import db
import json

class Gateway(db.Model):
    __tablename__ = 'gateway'

    id = Column(Integer, primary_key=True)
    hostname = Column(String, unique=True)
    status = Column(Boolean)
    last_heartbeat = Column(DateTime)

    def __init__(self, hostname, status, last_heartbeat):
        self.hostname = hostname
        self.status = status
        self.last_heartbeat = last_heartbeat

    @property
    def serialize(self):
        rules = Rule.query.filter_by(gateway_id=self.id).count()
        devices = Device.query.filter_by(gateway_id=self.id).count()
        data = {
            "id": self.id,
            "hostname": self.hostname,
            "status": "UP" if self.status else "DOWN",
            "last_heartbeat": self.last_heartbeat.strftime('%d-%m-%Y %H:%M'),
            "devices": devices,
            "rules" : rules,
        }
        return data

    def __repr__(self):
        return str(self.serialize)


class Rule(db.Model):
    __tablename__ = 'rule'

    id = Column(Integer, primary_key=True)
    r_id = Column(Integer, unique=True)
    gateway_id = Column(Integer, ForeignKey('gateway.id'))
    json_rule = Column(String)


    def __init__(self, r_id, gateway_id, json_rule):
        self.r_id = r_id
        self.gateway_id = gateway_id
        self.json_rule = json_rule

    @property
    def serialize(self):
        gateway = Gateway.query.filter_by(id=self.gateway_id).first()
        json_r = json.loads(self.json_rule)
        data = {
            "id": self.id,
            "r_id": self.r_id,
            "gateway_id": gateway.hostname if gateway else "None",
            "target" : str(json_r['actions'][0]['target']['topic']),
            "json_rule": self.json_rule,
        }
        return data

    def __repr__(self):
        return str(self.serialize)

class Device(db.Model):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    gateway_id = Column(Integer, ForeignKey('gateway.id'))

    def __init__(self, name, gateway_id):
        self.name = name
        self.gateway_id = gateway_id

    @property
    def serialize(self):
        gateway = Gateway.query.filter_by(id=self.gateway_id).first()
        data = {
            "id": self.id,
            "name": self.name,
            "gateway_id": gateway.hostname if gateway else "None",
            "type" : "fa fa-lightbulb-o fa-2x" if "light" in self.name else \
                    "fa fa-thermometer-three-quarters fa-2x" if "tmp" in self.name else \
                    "fa fa-tint fa-2x" if "hum" in self.name else \
                    "fa fa-exchange fa-2x" if "motion" in self.name else \
                    "fa fa-sun-o fa-2x"
        }
        return data

    def __repr__(self):
        return str(self.serialize)
