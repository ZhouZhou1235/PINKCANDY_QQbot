# 配置管理器

from core.data_models import BotConfig
from core.connect_database import MySQLConnecter
from core.chat_robot import MemoryChatRobot
from typing import Callable
from typing import Callable
from datetime import datetime, timedelta
import json
import os
import asyncio
import threading
import time
import schedule


class ScheduleTask:
    """定时任务"""
    def __init__(self):
        self.tasks = []
        self.running = True
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.loop_thread.start()
        self.schedule_thread = threading.Thread(target=self._run_pending, daemon=True)
        self.schedule_thread.start()
        self.task_counter = 0
    def _run_loop(self):
        """运行事件循环"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    def _run_pending(self):
        """运行定时任务检查"""
        while self.running:
            schedule.run_pending()
            time.sleep(0.1)
    def _run_async_task(self, task:Callable, *args, **kwargs):
        """运行异步任务"""
        if asyncio.iscoroutinefunction(task):
            asyncio.run_coroutine_threadsafe(task(*args, **kwargs), self.loop)
        else:
            task(*args, **kwargs)
    def schedule_task(self, delay:int, task:Callable, *args, **kwargs):
        """一次任务 延迟delay时间后执行"""
        self.task_counter += 1
        job_id = f"single_{self.task_counter}"
        def execute_once():
            self._run_async_task(task, *args, **kwargs)
            self.tasks = [t for t in self.tasks if t["id"] != job_id]
        timer = threading.Timer(delay, execute_once)
        timer.daemon = True
        timer.start()
        class MockJob:
            def __init__(self, job_id):
                self.id = job_id
                self.next_run = datetime.now() + timedelta(seconds=delay)
        mock_job = MockJob(job_id)
        self.tasks.append({"id": job_id, "job": mock_job, "timer": timer})
        return job_id
    def schedule_loop_task(self, interval:int, task:Callable, *args, **kwargs):
        """循环任务 每隔interval时间执行一次"""
        self.task_counter += 1
        job_id = f"loop_{self.task_counter}"
        job = schedule.every(interval).seconds.do(self._run_async_task, task, *args, **kwargs)
        self.tasks.append({"id": job_id, "job": job})
        return job_id
    def get_task_list(self):
        """获取任务列表"""
        result = []
        for task in self.tasks:
            if "timer" in task:
                if task["timer"].is_alive():
                    result.append({"id": task["id"], "next_run": task["job"].next_run})
            else:
                if task["job"] in schedule.jobs:
                    result.append({"id": task["id"], "next_run": task["job"].next_run})
        return result
    def cancel_task(self, job_id:str):
        """取消任务"""
        for task in self.tasks:
            if task["id"] == job_id:
                if "timer" in task:
                    task["timer"].cancel()
                else:
                    schedule.cancel_job(task["job"])
                self.tasks.remove(task)
                break
    def cancel_all_tasks(self):
        """取消所有任务"""
        for task in self.tasks:
            if "timer" in task:
                task["timer"].cancel()
        schedule.clear()
        self.tasks.clear()
        self.running = False
        self.loop.call_soon_threadsafe(self.loop.stop)

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
        self.work_path = os.getcwd()
        # self.work_path = os.getcwd() + '/bot' # 用 vscode F5运行
        self.config_path = self.work_path.replace("\\", "/") + "/bot_config.json"
        with open(self.config_path, 'r', encoding='UTF-8') as f: config_data=json.load(f)
        # 全局变量
        self.bot_config = BotConfig.load(config_data) # 配置
        self.mysql_connector = MySQLConnecter(self.bot_config) # MySQL连接者
        self.chat_robot = MemoryChatRobot(self.bot_config,self.mysql_connector) # 聊天机器人
        self.date_scheduler = ScheduleTask() # 日期定时任务
        self.message_scheduler = ScheduleTask() # 消息定时任务

config_manager = ConfigManager()
