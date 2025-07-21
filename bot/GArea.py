# 全局空间

import random
import time
from typing import Any, List
from core.ai_chat import MemoryChatRobot
from core.bot_config import Config
from functools import wraps
from ncatbot.core import GroupMessage

# === 固定量 ===
GALLERY_SYSTEM_WEB = "https://gallery-system.pinkcandy.top"
GALLERY_WEB = "https://gallery.pinkcandy.top"
DEEPSEEK_API = "https://api.deepseek.com"
DEEPSEEK_API_KEY = "sk-69d85f5be9184810970ccf2d4add0474"


# === 函数 ===

# 得到指令对应的文本
def getCommendString(commendKey:str):
    return f"{Config().fixed_begin} {Config().function_commands[commendKey]}"

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


# === 类 ===

# 事件冷却
class EventCoolDown:
    # 用法
    # 实例化 用作函数的修饰器
    # eventCoolDown = EventCoolDown(5)
    # @eventCoolDown
    # def func(message): pass
    def __init__(self,interval):
        self.interval = interval # 冷却时间
        self.last_trigger = {}
    def __call__(self,func:Any):
        @wraps(func)
        async def wrapper(message: GroupMessage,*args,**kwargs):
            command = getCommendString(func.__name__)
            # 放行非目标命令
            if not message.raw_message.startswith(command):
                return await func(message,*args,**kwargs)
            key = f"{message.group_id}_{func.__name__}"
            now = time.time()
            if key in self.last_trigger and now - self.last_trigger[key] < self.interval:
                await message.reply("PINKCANDY: too fast! wait a few seconds.")
                return
            self.last_trigger[key] = now
            return await func(message, *args, **kwargs)
        return wrapper


# === 变量 ===
g_bot_config = Config()
g_memoryChatRobot = MemoryChatRobot(DEEPSEEK_API,DEEPSEEK_API_KEY)
g_eventCoolDown = EventCoolDown(5)
