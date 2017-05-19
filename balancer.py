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
import atexit

topics_list = {} #All topics and their devices
gateways = {} #Device - Gateway
device_topics = {} #Device - Topic
gateway_devices = {} #Gateway - Num devices
gateway_timestamp = {} #Gateways that are up
on_gateways = [] # Online gateways
rule_id_gateway = {} #Rule id -> Gateway

loader = RuleLoader(confs.RULES_FOLDER)
executer = ThreadPoolExecutor(max_workers=confs.WORKERS)
test = {}
def main():

    executer.submit(check_hb)
    loader.process_rules()
    subscribe.callback(on_message, ["/SM/in_events/#", "/SM/out_events/#", "/SM/devconfig", "/SM/devices/#", "/SM/regdevice", "/SM/hb/"], hostname="localhost")

def on_message(client, userdata, msg):

    executer.submit(process_message, client, userdata, msg)

def process_message(client, userdata, msg):

    global topics_list
    global gateways
    global device_topics
    global gateway_devices

    if msg.topic == '/SM/devconfig':
        publish.single(msg.topic, payload=msg.payload, qos=1, retain=False,
        hostname=confs.SCOT_BROKER, port=1883, client_id="", keepalive=60,
        will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

    elif msg.topic == '/SM/regdevice':
        message = json.loads(msg.payload.decode("utf-8"))

        if message['device'] in gateways:

            if message['gateway'] not in gateway_devices:
                gateway_devices[message['gateway']]=0

            if gateway_devices[gateways[message['device']][0]] > gateway_devices[message['gateway']]:
                gateway_devices[message['gateway']]+=1
                gateway_devices[gateways[message['device']][0]]-=1
                ##Warn gateways
                try:
                    publish.single("/SM/add_device", payload=message['device'], qos=1, retain=False,
                                hostname=""+message['gateway']+".local", port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
                    publish.single("/SM/delete_device", payload=message['device'], qos=1, retain=False,
                                hostname=""+gateways[message['device']][0]+".local", port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
                except Exception as e:
                    print(e)
                #Insert gateway in the preferencial position
                gateways[message['device']].insert(0,message['gateway'])

            else:

                gateways[message['device']].append(message['gateway'])

        else:
            gateways[message['device']] = [message['gateway']]

            if message['gateway'] not in gateway_devices:
                gateway_devices[message['gateway']]=0

            gateway_devices[message['gateway']]+=1
            publish.single("/SM/add_device", payload=message['device'], qos=1, retain=False,
                                hostname=""+message['gateway']+".local", port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)


    elif "/SM/devices/" in msg.topic:

        message = json.loads(msg.payload.decode("utf-8"))
        device = msg.topic.replace("/SM/devices/", "")

        if "motion" in device:
            return

        if message['operation']['metaData']['operation'] == "add_publish_topic":
            topic = message['operation']['payloadData']['value'].replace("in_events","out_events")
            device_topics[device] = topic

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

        for topic, regex in topics_list.items():
            if regex[0].match(msg.topic):
                for dev in regex[1]:
                    publish.single(device_topics[dev], payload=msg.payload, qos=1, retain=False,
                                hostname=""+gateways[dev][0]+".local", port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

    elif "/SM/in_events/" in msg.topic:

        ### THIS WIL PUBLISH ON SCOT ONLY LATER
        send_gateways = []
        for tpc in RuleLoader.regex_id:
            regex = re.compile(tpc)

            if re.match(regex, msg.topic):
                for r_id in RuleLoader.regex_id[tpc]:
                    for host in rule_id_gateway[r_id]:
                        send_gateways.append(host)

        send_gateways = set(send_gateways)

        for host in send_gateways:
            publish.single(msg.topic, payload=msg.payload, qos=1, retain=False,
                        hostname=host, port=1883, client_id="", keepalive=60,
                        will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

    elif "/SM/hb/" in msg.topic:
        global gateway_timestamp
        global on_gateways

        message = json.loads(msg.payload.decode("utf-8"))
        gateway_timestamp[message['gateway']] = time.time()

        if message['gateway'] not in on_gateways:
            if [item for item in on_gateways if item[0] == message['gateway']] == []:
                on_gateways.insert(0, (message['gateway'],[]))
                print("Adding gateway")

                # REQUEST GATEWAY DEVICES
                publish.single("/SM/send_devices", payload='', qos=1, retain=False,
                                hostname=message['gateway'], port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

                add_gateways()

def check_hb():

    global on_gateways
    global gateways
    global gateway_devices

    while True:
        try:
            for gtw in on_gateways:
                print('gtw '+str(gtw[0])+ " : "+ str(len(gtw[1])))
        except Exception as e:
            print (e)

        for gateway in gateway_timestamp:
            if time.time() - gateway_timestamp[gateway] > 10:
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

                                    publish.single("/SM/add_device", payload=device, qos=1, retain=False,
                                            hostname=gateways[device][0]+".local", port=1883, client_id="", keepalive=60,
                                            will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
                                    gateway_devices[gateways[device][0]]+=1
                                    gateway_devices[gtws]-=1

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
        print(rules_list)
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

    if add:
        publish.single("/SM/add_rule", payload='{"id": "'+str(rule_id)+'", "rule": ' +RuleLoader.rules[rule_id]+'}', qos=1, retain=False,
                                hostname=add, port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

        if rule_id in rule_id_gateway:
            rule_id_gateway[rule_id].append(add)
        else:
            rule_id_gateway[rule_id] = [add]


@atexit.register
def goodbye():

    print(gateway_devices)

if __name__ == '__main__':
    main()

