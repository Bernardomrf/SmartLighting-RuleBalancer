import configs as confs
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time

def main():
    DEVICE_AC = []
    DEVICE_TMP = []
    DEVICE_HUM = []
    DEVICE_LUX = []
    DEVICE_MOTION = []
    DEVICE_LIGHT = []
    DEVICE_LIGHT_B = []
    DEVICE_LIGHT_C = []
    DEVICE_LIGHT_S = []

    """
    for i in range(1,46):
        DEVICES.append('ac%d'%i)

    for i in range(1,50):
        DEVICES.append('tmp%d'%i)


    for i in range(1,50):
        DEVICES.append('hum%d'%i)

    """
    for i in range(1,157):
        DEVICE_LUX.append('lux%d'%i)


    for i in range(1,165):
        DEVICE_MOTION.append('motion%d'%i)


    for i in range(1,109):
        DEVICE_LIGHT.append('light%d'%i)

    """
    for i in range(1,34):
        DEVICES.append('light_b%d'%i)


    for i in range(1,10):
        DEVICES.append('light_s%d'%i)
    """

    for i in range(1,77):
        DEVICE_LIGHT_C.append('light_c%d'%i)



    for device in DEVICE_MOTION:
        data ='{"objects": [{"object_id": 3, "object_instance": 0, "resources": [{"resource_instance": 0, "resource_id": 11}, {"resource_instance": 0, "resource_id": 16}, {"resource_instance": 0, "resource_id": 4}]}, {"object_id": 1, "object_instance": 0, "resources": [{"resource_instance": 0, "resource_id": 1}, {"resource_instance": 0, "resource_id": 8}, {"resource_instance": 0, "resource_id": 7}, {"resource_instance": 0, "resource_id": 6}, {"resource_instance": 0, "resource_id": 0}]}, {"object_id": 3302, "object_instance": 0, "resources": [{"resource_instance": 0, "resource_id": 5500}]}, {"object_id": 1301, "object_instance": 0, "resources": [{"resource_instance": 0, "resource_id": 13011}, {"resource_instance": 0, "resource_id": 13015}, {"resource_instance": 0, "resource_id": 13014}, {"resource_instance": 0, "resource_id": 13013}, {"resource_instance": 0, "resource_id": 13012}]}], "device": {"device_id": "'+ device +'"}}'
        publish.single('/SM/devconfig', payload=str.encode(data), qos=1, retain=False,
            hostname="sonata5.local", port=1883, client_id="", keepalive=60,
            will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
        time.sleep(0.2)

    for device in DEVICE_LIGHT_C:
        data ='{"device": {"device_id": "'+ device +'"}, "objects": [{"object_id": 3, "object_instance": 0, "resources": [{"resource_instance": 0, "resource_id": 11}, {"resource_instance": 0, "resource_id": 16}, {"resource_instance": 0, "resource_id": 4}]}, {"object_id": 1, "object_instance": 0, "resources": [{"resource_instance": 0, "resource_id": 1}, {"resource_instance": 0, "resource_id": 8}, {"resource_instance": 0, "resource_id": 7}, {"resource_instance": 0, "resource_id": 6}, {"resource_instance": 0, "resource_id": 0}]}, {"object_id": 1501, "object_instance": 0, "resources": [{"resource_instance": 0, "resource_id": 15011}, {"resource_instance": 0, "resource_id": 15014}, {"resource_instance": 0, "resource_id": 15013}, {"resource_instance": 0, "resource_id": 15012}]}, {"object_id": 1301, "object_instance": 0, "resources": [{"resource_instance": 0, "resource_id": 13011}, {"resource_instance": 0, "resource_id": 13015}, {"resource_instance": 0, "resource_id": 13014}, {"resource_instance": 0, "resource_id": 13013}, {"resource_instance": 0, "resource_id": 13012}]}]}'
        publish.single('/SM/devconfig', payload=str.encode(data), qos=1, retain=False,
            hostname="sonata5.local", port=1883, client_id="", keepalive=60,
            will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
        time.sleep(0.2)

    for device in DEVICE_LIGHT:
        data ='{"device": {"device_id": "'+device+'"}, "objects": [{"object_id": 3, "object_instance": 0, "resources": [{"resource_instance": 0, "resource_id": 11}, {"resource_instance": 0, "resource_id": 16}, {"resource_instance": 0, "resource_id": 4}]}, {"object_id": 1, "object_instance": 0, "resources": [{"resource_instance": 0, "resource_id": 1}, {"resource_instance": 0, "resource_id": 8}, {"resource_instance": 0, "resource_id": 7}, {"resource_instance": 0, "resource_id": 6}, {"resource_instance": 0, "resource_id": 0}]}, {"object_id": 1501, "object_instance": 0, "resources": [{"resource_instance": 0, "resource_id": 15011}, {"resource_instance": 0, "resource_id": 15014}, {"resource_instance": 0, "resource_id": 15013}, {"resource_instance": 0, "resource_id": 15012}]}, {"object_id": 1301, "object_instance": 0, "resources": [{"resource_instance": 0, "resource_id": 13011}, {"resource_instance": 0, "resource_id": 13015}, {"resource_instance": 0, "resource_id": 13014}, {"resource_instance": 0, "resource_id": 13013}, {"resource_instance": 0, "resource_id": 13012}]}]}'
        publish.single('/SM/devconfig', payload=str.encode(data), qos=1, retain=False,
            hostname="sonata5.local", port=1883, client_id="", keepalive=60,
            will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
        time.sleep(0.2)

    for device in DEVICE_LUX:
        data ='{"device": {"device_id": "'+device+'"}, "objects": [{"resources": [{"resource_id": 11, "resource_instance": 0}, {"resource_id": 16, "resource_instance": 0}, {"resource_id": 4, "resource_instance": 0}], "object_instance": 0, "object_id": 3}, {"resources": [{"resource_id": 1, "resource_instance": 0}, {"resource_id": 8, "resource_instance": 0}, {"resource_id": 7, "resource_instance": 0}, {"resource_id": 6, "resource_instance": 0}, {"resource_id": 0, "resource_instance": 0}], "object_instance": 0, "object_id": 1}, {"resources": [{"resource_id": 5700, "resource_instance": 0}], "object_instance": 0, "object_id": 3301}, {"resources": [{"resource_id": 13011, "resource_instance": 0}, {"resource_id": 13015, "resource_instance": 0}, {"resource_id": 13014, "resource_instance": 0}, {"resource_id": 13013, "resource_instance": 0}, {"resource_id": 13012, "resource_instance": 0}], "object_instance": 0, "object_id": 1301}]}'

        publish.single('/SM/devconfig', payload=str.encode(data), qos=1, retain=False,
            hostname="sonata5.local", port=1883, client_id="", keepalive=60,
            will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)
        time.sleep(0.2)

if __name__ == '__main__':
    main()
