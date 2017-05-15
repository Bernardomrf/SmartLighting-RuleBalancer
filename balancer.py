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
alive_gateways = {} #Gateways that are up
gateways_rules = {} #gateways and number of rules


loader = RuleLoader(confs.RULES_FOLDER)
executer = ThreadPoolExecutor(max_workers=confs.WORKERS)
test = {}
def main():

    executer.submit(check_hb)
    loader.process_rules()
    subscribe.callback(on_message, ["/SM/in_events/#", "/SM/out_events/#", "/SM/devconfig", "/SM/devices/#", "/SM/regdevice"], hostname="localhost")

def on_message(client, userdata, msg):
    executer.submit(process_message, client, userdata, msg)

def process_message(client, userdata, msg):
    global topics_list
    global gateways
    global device_topics
    global gateway_devices

    if msg.topic == '/SM/devconfig':
        #print(msg.payload)
        publish.single(msg.topic, payload=msg.payload, qos=1, retain=False,
        hostname=confs.SCOT_BROKER, port=1883, client_id="", keepalive=60,
        will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

    elif msg.topic == '/SM/regdevice':

        message = json.loads(msg.payload.decode("utf-8"))
        #print(message)
        if message['device'] in gateways:
            if message['gateway'] not in gateway_devices:
                #print('novo device nao existe')
                gateway_devices[message['gateway']]=0

            if gateway_devices[gateways[message['device']][0]] > gateway_devices[message['gateway']]:
                #print('troca')
                gateway_devices[message['gateway']]+=1
                gateway_devices[gateways[message['device']][0]]-=1

                ##Warn gateways
                try:
                    publish.single("/SM/add_device", payload=message['device'], qos=0, retain=False,
                                hostname=""+message['gateway']+".local", port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
                    publish.single("/SM/delete_device", payload=message['device'], qos=0, retain=False,
                                hostname=""+gateways[message['device']][0]+".local", port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
                except Exception as e:
                    print(e)


                #Insert gateway in the preferencial position
                gateways[message['device']].insert(0,message['gateway'])
            else:
                gateways[message['device']].append(message['gateway'])

        else:
            #print ('else')
            gateways[message['device']] = [message['gateway']]
            if message['gateway'] not in gateway_devices:
                gateway_devices[message['gateway']]=0
            gateway_devices[message['gateway']]+=1


            publish.single("/SM/add_device", payload=message['device'], qos=0, retain=False,
                                hostname=""+message['gateway']+".local", port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)


    elif "/SM/devices/" in msg.topic:
        #print (msg.topic)
        message = json.loads(msg.payload.decode("utf-8"))
        device = msg.topic.replace("/SM/devices/", "")

        if "motion" in device:
            '''if message['operation']['metaData']['operation'] == "add_publish_topic":
                                                    test[device] = message['operation']['payloadData']['value'] + '/3302/all/5500/all'
                                                    print(message['operation']['payloadData']['value'])'''
            return


        if message['operation']['metaData']['operation'] == "add_publish_topic":

            topic = message['operation']['payloadData']['value'].replace("in_events","out_events")
            device_topics[device] = topic
            #print(device_topics[device])

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

        #print("Topic: " + msg.topic)
        for topic, regex in topics_list.items():
            if regex[0].match(msg.topic):
                for dev in regex[1]:
                    publish.single(device_topics[dev], payload=msg.payload, qos=0, retain=False,
                                hostname=""+gateways[dev][0]+".local", port=1883, client_id="", keepalive=60,
                                will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
                    #print("Devices: " + gateways[dev][0])

    elif "/SM/in_events/" in msg.topic:

        ### THIS WIL PUBLISH ON SCOT ONLY
        #for topic in loader.rule_gateway:
            #print(topic)
        #regex = ure.compile(reg_topic)
        #print(test)
        #print (RuleLoader.rule_gateway)
        for tpc in RuleLoader.rule_gateway:
            regex = re.compile(tpc)

            #print('publish1')
            if re.match(regex, msg.topic):
                #print('publish2')
                for host in RuleLoader.rule_gateway[tpc]:

                    #print('publish')
                    publish.single(msg.topic, payload=msg.payload, qos=0, retain=False,
                    hostname=host, port=1883, client_id="", keepalive=60,
                    will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

    elif "/SM/hb/" in msg.topic:
        global alive_gateways

        message = json.loads(msg.payload.decode("utf-8"))
        alive_gateways[message['gateway']] = (time.time(),True)


def check_hb():
    gate_on = []
    global alive_gateways
    for gateway in alive_gateways:
        if time.time() - alive_gateways[gateway] > 10:
            alive_gateways[gateway][1] = False
        else:
            gate_on.append(gateway)
    balance_gateways(gate_on)
    time.sleep(10)

def balance_gateways(gate_on):
    if len(gate_on) != len(gateways_rules):

        pass
    pass

@atexit.register
def goodbye():
    #print(topics_list)
    print(RuleLoader.rule_gateway)
    print(RuleLoader.rules)
    print(gateway_devices)
    #print(device_topics)


if __name__ == '__main__':
    main()

