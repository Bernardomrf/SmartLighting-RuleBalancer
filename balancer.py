# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
from concurrent.futures import ThreadPoolExecutor
from rule_loader import RuleLoader
import configs as confs
import time
import json
import re



topics_list = {} #All topics and their devices
gateways = {} #Device - Gateway
device_topics = {} #Device - Topic
loader = RuleLoader(confs.RULES_FOLDER)
loader.process_rules()
executer = ThreadPoolExecutor(max_workers=10)

def on_message(client, userdata, msg):
    executer.submit(process_message, client, userdata, msg)

def process_message(client, userdata, msg):

    global topics_list
    global gateways
    global device_topics

    if msg.topic == '/SM/devconfig':
        #print(msg.payload)
        publish.single(msg.topic, payload=msg.payload, qos=0, retain=False,
        hostname="sonata5.local", port=1883, client_id="", keepalive=60,
        will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

    elif msg.topic == '/SM/regdevice':

        message = json.loads(msg.payload.decode("utf-8"))
        if message['device'] in gateways:
            gateways[message['device']].append(message['gateway'])
        else:
            gateways[message['device']] = [message['gateway']]

    elif "/SM/devices/" in msg.topic:
        message = json.loads(msg.payload.decode("utf-8"))
        device = msg.topic.replace("/SM/devices/", "")

        if "motion" in device:
            return

        if message['operation']['metaData']['operation'] == "add_publish_topic":

            topic = message['operation']['payloadData']['value'].replace("in_events","out_events")
            device_topics[device] = topic
            print(device_topics[device])

        elif message['operation']['metaData']['operation'] == "subscribe_topic":

            topics = message['operation']['payloadData']['value'].split(';')
            for topic in topics:
                topic = topic.replace("/#","/.*")
                if topic in topics_list:
                    if device in topics_list[topic][1]:
                        continue
                    topics_list[topic][1].append(device)
                else:
                    topics_list[topic] = (re.compile(topic),[device])

    elif "/SM/out_events/" in msg.topic:

        print("Topic: " + msg.topic)
        for topic, regex in topics_list.items():
            if regex[0].match(msg.topic):
                for dev in regex[1]:
                    publish.single(device_topics[dev], payload=msg.payload, qos=0, retain=False,
                                hostname=""+gateways[dev][0]+".local", port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
                    print("Devices: " + gateways[dev][0])

    elif "/SM/in_events/" in msg.topic:
        #for topic in loader.rule_gateway:
            #print(topic)
        #regex = ure.compile(reg_topic)
        print (RuleLoader.rule_gateway)
        for tpc in RuleLoader.rule_gateway:
            regex = re.compile(tpc)


            if re.match(regex, msg.topic):

                for host in RuleLoader.rule_gateway[tpc]:

                    print('publish')
                    publish.single(msg.topic, payload=msg.payload, qos=0, retain=False,
                    hostname=host, port=1883, client_id="", keepalive=60,
                    will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

subscribe.callback(on_message, ["/SM/in_events/#", "/SM/out_events/#", "/SM/devconfig", "/SM/devices/#", "/SM/regdevice"], hostname="localhost")

