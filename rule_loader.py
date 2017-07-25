
import os
import json
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import itertools
import re
import requests
import configs as confs


class RuleLoader:


    regex_id = {}
    target_rule_id = {}
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

    def load_json(data):
        global count
        for subrule in data['subrules']:
            data={}
            RuleLoader.count += 1
            for action in subrule['actions']:
                target = '/SM' + action['target']['topic']

                if RuleLoader.count in RuleLoader.target_rule_id:
                    RuleLoader.target_rule_id[RuleLoader.count].append(target)
                else:
                    RuleLoader.target_rule_id[RuleLoader.count] = [target]


                if action['function']['name'] == 'set_value':
                    for listener in action['function']['listen_data']['listeners']:
                        l = '/SM'+listener['topic']#.replace("/+","/[^/]+")
                        if l in RuleLoader.regex_id:
                            if RuleLoader.count in RuleLoader.regex_id[l]:
                                continue
                            RuleLoader.regex_id[l].append(RuleLoader.count)
                        else:
                            RuleLoader.regex_id[l] = [RuleLoader.count]

                elif action['function']['name'] == 'setif_value_percent':
                    for listener in action['function']['listen_value']['listeners']:
                        l = '/SM'+listener['topic']#.replace("/+","/[^/]+")
                        if l in RuleLoader.regex_id:
                            if RuleLoader.count in RuleLoader.regex_id[l]:
                                continue
                            RuleLoader.regex_id[l].append(RuleLoader.count)
                        else:
                            RuleLoader.regex_id[l] = [RuleLoader.count]

                    for listener in action['function']['listen_boolean']['listeners']:
                        l = '/SM'+listener['topic']#.replace("/+","/[^/]+")
                        if l in RuleLoader.regex_id:
                            if RuleLoader.count in RuleLoader.regex_id[l]:
                                continue
                            RuleLoader.regex_id[l].append(RuleLoader.count)
                        else:
                            RuleLoader.regex_id[l] = [RuleLoader.count]


            RuleLoader.rules[RuleLoader.count] = json.dumps(subrule)
            try:
                data['id'] = RuleLoader.count
                data['rule'] = json.dumps(subrule)
                req =  requests.post(confs.ADD_RULE_URL, data=data)

            except Exception as e:
                print(e)










