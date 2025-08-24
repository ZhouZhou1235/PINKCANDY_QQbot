# 配置管理器

from collections import namedtuple
import heapq
import json
import os
import asyncio
import threading
import time
from typing import Callable
from core.data_models import BotConfig
from core.connect_database import MySQLConnecter
from core.chat_robot import MemoryChatRobot


# 定义定时任务结构
ScheduledTask = namedtuple('ScheduledTask', ['next_run', 'interval', 'func', 'loop', 'task_id'])

# 定时任务
class Scheduler:
    def __init__(self):
        self.tasks = []
        self.task_counter = 0
        self.active = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    def _run(self):
        while self.active:
            try:
                now = time.time()
                with self.lock:
                    while self.tasks and self.tasks[0].next_run <= now:
                        task = heapq.heappop(self.tasks)
                        try:
                            result = task.func()
                            if asyncio.iscoroutine(result):
                                asyncio.run_coroutine_threadsafe(result, self.loop)
                        except Exception as e: print(e)
                        if task.loop:
                            next_run = task.next_run + task.interval
                            while next_run <= now:
                                next_run += task.interval
                            new_task = ScheduledTask(
                                next_run=next_run,
                                interval=task.interval,
                                func=task.func,
                                loop=task.loop,
                                task_id=task.task_id
                            )
                            heapq.heappush(self.tasks, new_task)
                time.sleep(0.1)
            except Exception as e:
                print(e)
                time.sleep(1)
    # 设置定时任务
    def schedule_task(self, func: Callable, delay: float, loop=False, begin_time=None, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        if begin_time is None:
            begin_time = time.time()
        def wrapped_func():
            try:
                if asyncio.iscoroutinefunction(func):
                    async def async_wrapper():
                        return await func(*args, **kwargs)
                    asyncio.run_coroutine_threadsafe(async_wrapper(), self.loop)
                else:
                    return func(*args, **kwargs)
            except Exception as e: print(e)
        with self.lock:
            self.task_counter += 1
            task_id = self.task_counter
            first_run = begin_time + delay
            task = ScheduledTask(
                next_run=first_run,
                interval=delay,
                func=wrapped_func,
                loop=loop,
                task_id=task_id
            )
            heapq.heappush(self.tasks, task)
            return task_id
    # 取消所有定时任务
    def clear_all_tasks(self):
        with self.lock:
            self.tasks = []
            self.task_counter = 0
    # 停止定时任务
    def stop_scheduler(self):
        self.clear_all_tasks()
        self.active = False
        if self.loop.is_running():
            self.loop.stop()

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
        # 全局变量
        self.bot_config = BotConfig.load(config_data) # 配置
        self.mysql_connector = MySQLConnecter(self.bot_config) # MySQL连接者
        self.chat_robot = MemoryChatRobot(self.bot_config,self.mysql_connector) # 聊天机器人
        self.date_scheduler = Scheduler() # 日期定时任务
        self.message_scheduler = Scheduler() # 消息定时任务

config_manager = ConfigManager()
