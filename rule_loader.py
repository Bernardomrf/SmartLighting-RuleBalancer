
import os
import json
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import itertools
import re


class RuleLoader:

    gateways = ["gateway-pi.local","gateway-pi2.local", "sonata9.local", "sonata10.local"]
    round_robin = itertools.cycle(gateways)
    rule_gateway = {}

    def __init__(self, path):
        self.path = path

    def process_rules(self):
        print('Loading Rules')

        for filename in os.listdir(self.path):
            #print(filename)
            if filename.endswith(".json"):

                with open(self.path + filename) as data_file:
                    RuleLoader.load_json(json.load(data_file))
        print('Done loading rules')

    def load_json(data):

        for subrule in data['subrules']:
            host = next(RuleLoader.round_robin)
            for action in subrule['actions']:

                if action['function']['name'] == 'set_value':
                    for listener in action['function']['listen_data']['listeners']:
                        l = '/SM'+listener['topic'].replace("/+","/[^/]+")
                        if l in RuleLoader.rule_gateway:
                            if host in RuleLoader.rule_gateway[l]:
                                continue
                            RuleLoader.rule_gateway[l].append(host)
                        else:
                            RuleLoader.rule_gateway[l] = [host]

                elif action['function']['name'] == 'setif_value_percent':
                    for listener in action['function']['listen_value']['listeners']:
                        l = '/SM'+listener['topic'].replace("/+","/[^/]+")
                        if l in RuleLoader.rule_gateway:
                            if host in RuleLoader.rule_gateway[l]:
                                continue
                            RuleLoader.rule_gateway[l].append(host)
                        else:
                            RuleLoader.rule_gateway[l] = [host]

                    for listener in action['function']['listen_boolean']['listeners']:
                        l = '/SM'+listener['topic'].replace("/+","/[^/]+")
                        if l in RuleLoader.rule_gateway:
                            if host in RuleLoader.rule_gateway[l]:
                                continue
                            RuleLoader.rule_gateway[l].append(host)
                        else:
                            RuleLoader.rule_gateway[l] = [host]

            publish.single("/SM/rule", payload=json.dumps(subrule), qos=0, retain=False,
                    hostname=host, port=1883, client_id="", keepalive=60,
                    will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)



