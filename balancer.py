# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
from concurrent.futures import ThreadPoolExecutor
from rule_loader import RuleLoader
import requests
from datetime import datetime

import configs as confs
import time
import json
import re
import atexit

topics_list = {} #All topics and their devices
gateways = {} #Device - Gateway
device_topics = {} #Device - Topic
gateway_devices = {} #Gateway - Num devices
gateway_timestamp = {} #Gateways that are up
on_gateways = [] # Online gateways
rule_id_gateway = {} #Rule id -> Gateway
sensors = ['motion', 'lux', 'hum', 'tmp']

toggles=[]

loader = RuleLoader(confs.RULES_FOLDER)
executer = ThreadPoolExecutor(max_workers=confs.WORKERS)
test = {}
def main():

    executer.submit(check_hb)
    #executer.submit(scotListener)
    executer.submit(sendToggles)
    loader.process_rules()
    subscribe.callback(on_message, ["/SM/out_events/#", "/SM/devconfig", "/SM/regdevice", "/SM/hb/", "/signalOn", "/signalOff", "/SM/devices/#", "/SM/in_events/#"], qos=1, hostname="localhost", client_id="localBroker")


def on_message(client, userdata, msg):

    executer.submit(process_message, client, userdata, msg)

def process_message(client, userdata, msg):

    global topics_list
    global gateways
    global device_topics
    global gateway_devices
    global toggles
    global sensors

    if msg.topic == '/SM/devconfig':
        publish.single(msg.topic, payload=msg.payload, qos=1, retain=False,
        hostname=confs.SCOT_BROKER, port=1883, client_id="", keepalive=60,
        will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

    elif msg.topic == '/SM/regdevice':
        message = json.loads(msg.payload.decode("utf-8"))
        data = {}
        if message['device'] in gateways:

            if message['gateway'] not in gateway_devices:
                gateway_devices[message['gateway']]=0

            if gateway_devices[gateways[message['device']][0]] > gateway_devices[message['gateway']]:
                gateway_devices[message['gateway']]+=1
                gateway_devices[gateways[message['device']][0]]-=1
                ##Warn gateways
                try:

                    payload = json.dumps({message['device'] : topics_list[message['device']]})

                    publish.single("/SM/add_device", payload=payload, qos=1, retain=False,
                                hostname=""+message['gateway']+".local", port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
                    publish.single("/SM/delete_device", payload=message['device'], qos=1, retain=False,
                                hostname=""+gateways[message['device']][0]+".local", port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

                    data['gateway'] = message['gateway']
                    data['name'] = message['device']
                    req =  requests.post(confs.ADD_DEVICE_URL, data=data)

                except Exception as e:
                    print(e)
                #Insert gateway in the preferencial position
                gateways[message['device']].insert(0,message['gateway'])

            else:

                gateways[message['device']].append(message['gateway'])

                payload = json.dumps({message['device'] : topics_list[message['device']]})

                publish.single("/SM/add_device", payload=payload, qos=1, retain=False,
                                hostname=""+message['gateway']+".local", port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

        else:
            gateways[message['device']] = [message['gateway']]

            if message['gateway'] not in gateway_devices:
                gateway_devices[message['gateway']]=0

            gateway_devices[message['gateway']]+=1

            """payload = json.dumps({message['device'] : topics_list[message['device']]})
            publish.single("/SM/add_device", payload=payload, qos=1, retain=False,
                                hostname=""+message['gateway']+".local", port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)"""

            data['gateway'] = message['gateway']
            data['name'] = message['device']
            req =  requests.post(confs.ADD_DEVICE_URL, data=data)


    elif "/SM/devices/" in msg.topic:

        message = json.loads(msg.payload.decode("utf-8"))
        device = msg.topic.replace("/SM/devices/", "")
        topics_list[device] = []

        if True in [ x in device for x in sensors]:
            return

        if message['operation']['metaData']['operation'] == "add_publish_topic":
            topic = message['operation']['payloadData']['value'].replace("in_events","out_events")
            device_topics[device] = topic
            #print(device)

        elif message['operation']['metaData']['operation'] == "subscribe_topic":
            topics = message['operation']['payloadData']['value'].split(';')

            for topic in topics:
                topics_list[device].append(topic)

            try:
                payload = json.dumps({device : topics_list[device]})
                publish.single("/SM/add_device", payload=payload, qos=1, retain=False,
                                hostname=gateways[device][0]+".local", port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
            except Exception as e:
                raise e



    elif "/SM/hb/" in msg.topic:
        global gateway_timestamp
        global on_gateways

        message = json.loads(msg.payload.decode("utf-8"))
        gateway_timestamp[message['gateway']] = time.time()

        if message['gateway'] not in on_gateways:

            if [item for item in on_gateways if item[0] == message['gateway']] == []:
                on_gateways.insert(0, (message['gateway'],[]))
                print("Adding gateway")
                try:
                    print(message['gateway'])
                    publish.single("/SM/send_devices", payload='', qos=1, retain=False,
                                hostname=message['gateway'], port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

                    add_gateways()
                    # SEND REFRESH PAGE
                    publish.single("/refresh", payload="1", qos=1, retain=False,
                        hostname="localhost", port=1883, client_id="", keepalive=60,
                        will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
                except Exception as e:
                    print(e)

                # REQUEST GATEWAY DEVICES

    elif msg.topic == '/signalOn':
        print(msg.payload.decode("utf-8") + ' : ON')
        toggles.remove(msg.payload.decode("utf-8"))

    elif msg.topic == '/signalOff':
        print(msg.payload.decode("utf-8") + ' : OFF')
        toggles.append(msg.payload.decode("utf-8"))


def scotListener():
    subscribe.callback(on_message, ["/SM/devices/#", "/SM/in_events/#"], qos=1, hostname="localhost", client_id="scotBroker")

def check_hb():

    global on_gateways
    global gateways
    global gateway_devices

    while True:
        #print(rule_id_gateway)
        try:
            #for gtw in on_gateways:
             #   print('gtw '+str(gtw[0])+ " : "+ str(len(gtw[1])))
            #print(on_gateways)
            refresh = False
            for gateway in gateway_timestamp:
                data = {}
                data['status'] = True
                if time.time() - gateway_timestamp[gateway] > 10:

                    data['status'] = False

                    if [item for item in on_gateways if item[0] == gateway]:
                        rules_list = [item[1] for item in on_gateways if item[0] == gateway]
                        [on_gateways.remove(item) for item in on_gateways if item[0] == gateway]

                        remove_gateways(rules_list[0])
                        ### APAGAR GATEWAY do rule_id_gateway
                        ## DELEGATE GATEWAY DDEVICES TO OTHER GATEWAYS
                        for device in gateways:
                            for i, gtws in enumerate(gateways[device]):
                                ## FEIO FEIO FEIO#########################################
                                if gtws + ".local" == gateway:
                                    del gateways[device][i]
                                    if i == 0:

                                        payload = json.dumps({device : topics_list[device]})
                                        publish.single("/SM/add_device", payload=payload, qos=1, retain=False,
                                                hostname=gateways[device][0]+".local", port=1883, client_id="", keepalive=60,
                                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
                                        gateway_devices[gateways[device][0]]+=1
                                        gateway_devices[gtws]-=1
                        refresh=True

                data['hostname'] = re.sub('\.local$', '', gateway)
                data['last_hb'] = str(datetime.fromtimestamp(gateway_timestamp[gateway]))
                for gtw in on_gateways:

                    if gtw[0] == gateway:

                        data['rules'] = str(len(gtw[1]))
                data['devices'] = gateway_devices[data['hostname']]

                req =  requests.post(confs.ADD_GTW_URL, data=data)


        except Exception as e:
                print (e)

        if refresh:
                    # SEND REFRESH PAGE
            publish.single("/refresh", payload="2", qos=1, retain=False,
                        hostname="localhost", port=1883, client_id="", keepalive=60,
                        will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

        time.sleep(10)

def balance_gateways():

    global on_gateways

    on_gateways = sorted(on_gateways, key=lambda x: len(x[1]))

def add_gateways():

    global on_gateways

    i = len(on_gateways)-1
    if i>0:
        while len(on_gateways[0][1]) < len(on_gateways[i][1]):
            rule_id = on_gateways[i][1].pop()
            on_gateways[0][1].append(rule_id)
            report(rule_id, on_gateways[0][0], on_gateways[i][0])
            i-=1
            if i == 0:
                i = len(on_gateways)-1
        balance_gateways()
    else:
        on_gateways[0] = (on_gateways[0][0], list(RuleLoader.rules.keys()))
        for rule in on_gateways[0][1]:
            report(rule, add=on_gateways[0][0])


def remove_gateways(rules_list):

    global on_gateways

    try:
        #print(rules_list)
        for i in range(len(rules_list)):
            on_gateways[i%len(on_gateways)][1].append(rules_list[i])

            report(rules_list[i], add=on_gateways[i%len(on_gateways)][0])
    except Exception as e:
        print(e)


def report(rule_id, add=None, remove=None):

    global rule_id_gateway

    if remove:
        publish.single("/SM/remove_rule", payload=rule_id , qos=1, retain=False,
                                hostname=remove, port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
        rule_id_gateway[rule_id] = None

    if add:
        data={}
        data['hostname'] = re.sub('\.local$', '', add)
        data['id'] = rule_id
        req =  requests.post(confs.ADD_GTW_RULE_URL, data=data)

        publish.single("/SM/add_rule", payload='{"id": "'+str(rule_id)+'", "rule": ' +RuleLoader.rules[rule_id]+'}', qos=1, retain=False,
                                hostname=add, port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

        rule_id_gateway[rule_id] = add

def sendToggles():
    while True:
        global toggles
        #print(toggles)
        try:
            for item in toggles:
                publish.single("/heart_beat", payload="", qos=1, retain=False,
                hostname=str(item+".local"), port=1883, client_id="", keepalive=60,
                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
        except Exception as e:
            raise e

        time.sleep(5)

@atexit.register
def goodbye():
    print('****************** topics_list ******************')
    print(topics_list) #All topics and their devices
    #print('****************** gateways ******************')
    #print(gateways) #Device - Gateway
    #print('****************** device_topics ******************')
    #print(device_topics) #Device - Topic
    #print('****************** gateway_devices ******************')
    #print(gateway_devices) #Gateway - Num devices
    #print('****************** gateway_timestamp ******************')
    #print(gateway_timestamp) #Gateways that are up
    #print('****************** on_gateways ******************')
    #print(on_gateways) # Online gateways
    #print('****************** rule_id_gateway ******************')
    #print(rule_id_gateway) #Rule id -> Gateway
    #print('****************** regex_id ******************')
    #print(RuleLoader.regex_id)

if __name__ == '__main__':
    main()

