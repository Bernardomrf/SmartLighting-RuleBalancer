
import os
import json
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import itertools
import re


class RuleLoader:


    regex_id = {}
    rules = {}
    count = 0

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
        global count
        for subrule in data['subrules']:

            for action in subrule['actions']:

                if action['function']['name'] == 'set_value':
                    for listener in action['function']['listen_data']['listeners']:
                        l = '/SM'+listener['topic'].replace("/+","/[^/]+")
                        if l in RuleLoader.regex_id:
                            if RuleLoader.count in RuleLoader.regex_id[l]:
                                continue
                            RuleLoader.regex_id[l].append(RuleLoader.count)
                        else:
                            RuleLoader.regex_id[l] = [RuleLoader.count]

                elif action['function']['name'] == 'setif_value_percent':
                    for listener in action['function']['listen_value']['listeners']:
                        l = '/SM'+listener['topic'].replace("/+","/[^/]+")
                        if l in RuleLoader.regex_id:
                            if RuleLoader.count in RuleLoader.regex_id[l]:
                                continue
                            RuleLoader.regex_id[l].append(RuleLoader.count)
                        else:
                            RuleLoader.regex_id[l] = [RuleLoader.count]

                    for listener in action['function']['listen_boolean']['listeners']:
                        l = '/SM'+listener['topic'].replace("/+","/[^/]+")
                        if l in RuleLoader.regex_id:
                            if RuleLoader.count in RuleLoader.regex_id[l]:
                                continue
                            RuleLoader.regex_id[l].append(RuleLoader.count)
                        else:
                            RuleLoader.regex_id[l] = [RuleLoader.count]


            RuleLoader.rules[RuleLoader.count] = json.dumps(subrule)
            RuleLoader.count += 1
            #rule = '{"ID" : "'+ str(RuleLoader.count) +'", "rule":'+json.dumps(subrule)+'}'

            #publish.single("/SM/rule", payload=rule, qos=0, retain=False,
                    #hostname=host, port=1883, client_id="", keepalive=60,
                    #will=None, auth=None, tls=None, protocol=mqtt.MQTTv311)





