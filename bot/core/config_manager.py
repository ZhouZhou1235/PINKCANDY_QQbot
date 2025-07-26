# 配置管理器

import json
import os
from core.data_models import BotConfig
from core.connect_database import MySQLConnecter
from core.chat_robot import MemoryChatRobot


# 配置管理器
class ConfigManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    def __init__(self):
        if self._initialized: return
        self._initialized = True
        # 配置文件路径
        # self.work_path = os.getcwd() + '/bot' # 用 vscode F5运行
        self.work_path = os.getcwd()
        self.config_path = self.work_path.replace("\\", "/") + "/bot_config.json"
        with open(self.config_path, 'r', encoding='UTF-8') as f: config_data=json.load(f)
        self.bot_config = BotConfig.load(config_data)
        # 全局变量
        self.mysql_connector = MySQLConnecter(self.bot_config) # MySQL连接者
        self.chat_robot = MemoryChatRobot(self.bot_config,self.mysql_connector) # 聊天机器人


config_manager = ConfigManager()
