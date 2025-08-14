# 配置管理器

import json
import os
import asyncio
import threading
import time
from typing import Callable
from core.data_models import BotConfig
from core.connect_database import MySQLConnecter
from core.chat_robot import MemoryChatRobot


# 定时任务
class Scheduler:
    def __init__(self):
        self.tasks = []
        self.active = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        self.loop = asyncio.new_event_loop()
    def _run(self):
        while self.active:
            now = time.time()
            for task in self.tasks:
                if now>=task['time']:
                    try:
                        result = task['func']()
                        if asyncio.iscoroutine(result):
                            self.loop.run_until_complete(result)
                    except Exception as e:
                        print(e)
                    if task['loop']:
                        task['time'] = now+task['interval']
                    else:
                        self.tasks.remove(task)
            time.sleep(0.1)
    # 定时执行任务
    # args=(var1,) 逗号不可去除 表示元组
    def schedule_task(self,func:Callable,delay:float,loop=False,beginTime=time.time(),args=(),kwargs=None):
        if kwargs is None: kwargs={}
        async def wrapper():
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)
        self.tasks.append({
            'func': wrapper,
            'time': beginTime+delay,
            'interval': delay,
            'loop': loop
        })
    # 终止所有任务
    def stop_all_schedule(self):
        self.tasks.clear()
        self.active = False

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
        self.work_path = os.getcwd() + '/bot' # 用 vscode F5运行
        # self.work_path = os.getcwd()
        self.config_path = self.work_path.replace("\\", "/") + "/bot_config.json"
        with open(self.config_path, 'r', encoding='UTF-8') as f: config_data=json.load(f)
        # 全局变量
        self.bot_config = BotConfig.load(config_data) # 配置
        self.mysql_connector = MySQLConnecter(self.bot_config) # MySQL连接者
        self.chat_robot = MemoryChatRobot(self.bot_config,self.mysql_connector) # 聊天机器人
        self.scheduler = Scheduler() # 定时任务

config_manager = ConfigManager()
