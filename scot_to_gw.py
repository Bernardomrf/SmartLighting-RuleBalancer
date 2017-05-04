
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe

def on_message(client, userdata, msg):
    print(msg.payload)
    publish.single(msg.topic, payload=msg.payload, qos=1, retain=False,
    hostname="localhost", port=1883, client_id="", keepalive=60,
    will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

subscribe.callback(on_message, ["/SM/devices/#", "/SM/out_events/#"], hostname="sonata5.local")

