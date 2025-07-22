# -*-coding:utf-8 -*-
import yaml

# 配置文件
config_path = 'config/config.yml'
config_content = None


# 读取配置文件
def read_config_file(path=config_path):
    global config_content
    with open(path, 'r', encoding='utf-8') as file:
        config_content = yaml.safe_load(file)


# 登录账户密码
def read_credentials():
    if config_content and 'Credentials' in config_content and config_content['Credentials']:
        return config_content['Credentials']


# 获取测试目标
def read_urls():
    if config_content and 'Urls' in config_content and config_content['Urls']:
        return config_content['Urls']


# 获取维持登录字段
def read_login_parameters():
    if config_content and 'LoginParameters' in config_content and config_content['LoginParameters']:
        return config_content['LoginParameters']

def read_knowinfos():
    if config_content and 'KnowInfos' in config_content and config_content['KnowInfos']:
        return config_content['KnowInfos']
