import json


class ConfigService():

    def __init__(self):
        self.client_secrets = json.loads(open('client_secrets.json', 'r')
                                         .read())['web']

    def get_setting(self, setting):
        return self.client_secrets[setting]
