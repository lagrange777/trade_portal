import json


class ConfigManager:

    @staticmethod
    def get_port():
        with open('./configs_jsons/jsons/server_configs.json') as f:
            configs = json.load(f)
            port = configs['port']
        return port

    @staticmethod
    def get_db_address():
        with open('./configs_jsons/jsons/server_configs.json') as f:
            configs = json.load(f)
            db_address = configs['db_address']
        return db_address

    @staticmethod
    def get_db_login():
        with open('./configs_jsons/jsons/server_configs.json') as f:
            configs = json.load(f)
            db_login = configs['db_login']
        return db_login

    @staticmethod
    def get_db_password():
        with open('./configs_jsons/jsons/server_configs.json') as f:
            configs = json.load(f)
            db_password = configs['db_password']
        return db_password

    @staticmethod
    def get_db_name():
        with open('./configs_jsons/jsons/server_configs.json') as f:
            configs = json.load(f)
            db_address = configs['db_name']
        return db_address

    @staticmethod
    def get_host():
        with open('./configs_jsons/jsons/server_configs.json') as f:
            configs = json.load(f)
            host = configs['host']
        return host

    @staticmethod
    def get_debug():
        with open('./configs_jsons/jsons/server_configs.json') as f:
            configs = json.load(f)
            debug = configs['debug']
        return debug

    @staticmethod
    def get_secret_key():
        with open('./configs_jsons/jsons/server_configs.json') as f:
            configs = json.load(f)
            secret_key = configs['secret_key']
        return secret_key

    @staticmethod
    def get_company_name():
        with open('./configs_jsons/jsons/server_configs.json') as f:
            configs = json.load(f)
            company_name = configs['company_name']
        return company_name

    @staticmethod
    def get_server_version():
        with open('./configs_jsons/jsons/server_configs.json') as f:
            configs = json.load(f)
            server_version = configs['server_version']
        return server_version

    @staticmethod
    def get_key_word():
        with open('./configs_jsons/jsons/server_configs.json') as f:
            configs = json.load(f)
            key_word = configs['key_word']
        return key_word

    @staticmethod
    def get_integration_key():
        with open('./configs_jsons/jsons/server_configs.json') as f:
            configs = json.load(f)
            integration_key = configs['integration_key']
        return integration_key
