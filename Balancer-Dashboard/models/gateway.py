from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
from app import db

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
        data = {
            "id": self.id,
            "hostname": self.hostname,
            "status": "UP" if self.status else "DOWN",
            "last_heartbeat": self.last_heartbeat.strftime('%d-%m-%Y %H:%M'),
        }
        return data

    def __repr__(self):
        return str(self.serialize)


class Rule(db.Model):
    __tablename__ = 'rule'

    id = Column(Integer, primary_key=True)
    r_id = Column(Integer, primary_key=True)
    gateway_id = Column(Integer, ForeignKey('gateway.id'))
    json_rule = Column(String)


    def __init__(self, r_id, gateway_id, json_rule):
        self.r_id = r_id
        self.gateway_id = gateway_id
        self.json_rule = json_rule

    @property
    def serialize(self):
        data = {
            "id": self.id,
            "r_id": self.r_id,
            "gateway_id": self.gateway_id,
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
        data = {
            "id": self.id,
            "name": self.name,
            "gateway_id": self.gateway_id,
        }
        return data

    def __repr__(self):
        return str(self.serialize)
