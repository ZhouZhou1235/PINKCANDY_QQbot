# 全局通用工具

import asyncio
from functools import wraps
import random
import time
from typing import Any, Callable, List
from core.config_manager import config_manager
from ncatbot.core import GroupMessage,PrivateMessage
import threading
from datetime import datetime
from typing import Callable, Any


# 得到指令对应的文本
def getCommendString(commendKey:str):
    return f"{config_manager.bot_config.fixed_begin} {config_manager.bot_config.function_commands[commendKey]}"

# 从列表中抽取指定数量元素
def randomGetListElements(l:List[Any],num:int):
    theList = l.copy()
    resultList = []
    if num<0 or num>len(theList): return None
    while len(resultList)<num:
        i = random.randint(0,len(theList))
        element = theList[i]
        theList.pop(i)
        resultList.append(element)
    return resultList

# 读取文件为字符串
def readFileAsString(path:str):
    string = ''
    with open(path,mode='r',encoding='UTF-8') as f:
        string = f.read()
    return string

# 事件冷却修饰器
def eventCoolDown(seconds:int):
    def decorator(func:Callable):
        last_called = {} # 上次调用时间
        @wraps(func)
        async def wrapped(*args,**kwargs)->Any:
            message:GroupMessage|PrivateMessage = args[1] if len(args)>1 else kwargs.get('message') # type: ignore
            if not message: return None
            if hasattr(message,'group_id'):
                cooldown_key = f"group_{message.group_id}_{message.user_id}" # type: ignore
            else:
                cooldown_key = f"private_{message.user_id}"
            current_time = time.time()
            last_time = last_called.get(cooldown_key,0)
            if current_time-last_time<seconds:
                print(f"PINKCANDY COOLDOWN: too fast! wait {seconds - int(current_time-last_time)} second")
                return None
            last_called[cooldown_key] = current_time
            return await func(*args,**kwargs)
        return wrapped
    return decorator

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
    def schedule_task(self,func:Callable,delay:float,loop=False,args=(),kwargs=None):
        if kwargs is None: kwargs={}
        async def wrapper():
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)
        self.tasks.append({
            'func': wrapper,
            'time': time.time() + delay,
            'interval': delay,
            'loop': loop
        })
    # 指定时间执行任务
    def schedule_todo(self,func,daytime,args=(),kwargs=None):
        if kwargs is None: kwargs={}
        if isinstance(daytime, datetime):
            daytime = daytime.timestamp()
        async def wrapper():
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)
        self.tasks.append({
            'func': wrapper,
            'time': daytime,
            'interval': 0,
            'loop': False
        })
    # 终止所有任务
    def stop_all_schedule(self):
        self.tasks.clear()
        self.active = False
