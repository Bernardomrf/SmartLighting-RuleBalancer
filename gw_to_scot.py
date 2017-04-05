# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

def on_connect(client, userdata, rc):
    print ("Connected with result code " + str(rc))
    client.subscribe("#")


def on_message(client, userdata, msg):
    if msg.topic == '/SM/devconfig':
        publish.single(msg.topic, payload=msg.payload, qos=0, retain=False,
        hostname="gateway-pi2.local", port=1883, client_id="", keepalive=60,
        will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

client = mqtt.Client(client_id = "gw")
client.on_connect = on_connect
client.on_message = on_message
#client.username_pw_set("MQTTa79b9af9")
                       #password="3TQz4fkWoF22YnOQMPSKjqlkMQvlbMGz")

client.connect("gateway-pi.local", 1883, 60)
client.loop_forever()
