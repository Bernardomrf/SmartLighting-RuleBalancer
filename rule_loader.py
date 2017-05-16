
import os
import json
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import itertools
import re


class RuleLoader:

    gateways = ['none']#["gateway-pi.local","gateway-pi2.local", "sonata9.local", "sonata10.local"]
    round_robin = itertools.cycle(gateways)
    regex_id = {}
    rules = {}

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
        print(RuleLoader.regex_id)

    def load_json(data):
        count = 0
        for subrule in data['subrules']:
            host = next(RuleLoader.round_robin)
            for action in subrule['actions']:

                if action['function']['name'] == 'set_value':
                    for listener in action['function']['listen_data']['listeners']:
                        l = '/SM'+listener['topic'].replace("/+","/[^/]+")
                        if l in RuleLoader.regex_id:
                            if r_id in RuleLoader.regex_id[l]:
                                continue
                            RuleLoader.regex_id[l].append(count)
                        else:
                            RuleLoader.regex_id[l] = [count]

                elif action['function']['name'] == 'setif_value_percent':
                    for listener in action['function']['listen_value']['listeners']:
                        l = '/SM'+listener['topic'].replace("/+","/[^/]+")
                        if l in RuleLoader.regex_id:
                            if r_id in RuleLoader.regex_id[l]:
                                continue
                            RuleLoader.regex_id[l].append(count)
                        else:
                            RuleLoader.regex_id[l] = [count]

                    for listener in action['function']['listen_boolean']['listeners']:
                        l = '/SM'+listener['topic'].replace("/+","/[^/]+")
                        if l in RuleLoader.regex_id:
                            if r_id in RuleLoader.regex_id[l]:
                                continue
                            RuleLoader.regex_id[l].append(count)
                        else:
                            RuleLoader.regex_id[l] = [count]


            RuleLoader.rules[count] = json.dumps(subrule)
            count += 1
            #rule = '{"ID" : "'+ str(count) +'", "rule":'+json.dumps(subrule)+'}'

            #publish.single("/SM/rule", payload=rule, qos=0, retain=False,
                    #hostname=host, port=1883, client_id="", keepalive=60,
                    #will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)





