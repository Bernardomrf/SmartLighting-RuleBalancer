# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

def on_connect(client, userdata, rc):
    print ("Connected with result code " + str(rc))
    client.subscribe("/SM/devices/#")


def on_message(client, userdata, msg):

    publish.single(msg.topic, payload=msg.payload, qos=0, retain=False,
    hostname="gateway-pi.local", port=1883, client_id="", keepalive=60,
    will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)

client = mqtt.Client(client_id = "scot")
client.on_connect = on_connect
client.on_message = on_message
#client.username_pw_set("MQTTa79b9af9")
                       #password="3TQz4fkWoF22YnOQMPSKjqlkMQvlbMGz")

client.connect("gateway-pi2.local", 1883, 60)
client.loop_forever()

