# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe

def on_message(client, userdata, msg):
    publish.single(msg.topic, payload=msg.payload, qos=0, retain=False,
    hostname="sonata5.local", port=1883, client_id="", keepalive=60,
    will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

subscribe.callback(on_message, "/SM/devconfig", qos=1, hostname="localhost")
