# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
import json
import re

topics_list = {}


def on_message(client, userdata, msg):
    if msg.topic == '/SM/devconfig':
        publish.single(msg.topic, payload=msg.payload, qos=0, retain=False,
        hostname="sonata5.local", port=1883, client_id="", keepalive=60,
        will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

    elif "/SM/devices/" not in msg.topic:
        publish.single(msg.topic, payload=msg.payload, qos=0, retain=False,
        hostname="gateway-pi.local", port=1883, client_id="", keepalive=60,
        will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
        print(msg.topic)
        for regex in topics_list:
            if regex.match(msg.topic):
                print(topics_list[regex])
    else:

        message = json.loads(msg.payload.decode("utf-8"))
        if message['operation']['metaData']['operation'] == "subscribe_topic":
            global topics_list
            device = msg.topic.replace("/SM/devices/", "")
            print(device)

            topics = message['operation']['payloadData']['value'].split(';')
            for topic in topics:
                topic = topic.replace("/#","/.*")
                if topic in topics_list:
                    topics_list[re.compile(topic)].append(device)
                else:
                    topics_list[re.compile(topic)] = [device]


subscribe.callback(on_message, ["/SM/in_events/#", "/SM/out_events/#", "/SM/devconfig", "/SM/devices/#"], hostname="localhost")



