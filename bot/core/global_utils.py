# 全局通用工具

import asyncio
from functools import wraps
import random
import re
import time
import datetime
from typing import Any, Callable, List
from core.config_manager import config_manager
from ncatbot.core import GroupMessage,PrivateMessage
from typing import Callable, Any
from ncatbot.core import BotClient
from functions.share_functions import *


at_pattern = rf'\[CQ:at,qq={config_manager.bot_config.qq_number}\]|@{config_manager.bot_config.bot_name}|@{config_manager.bot_config.qq_number}'

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

# 识别 @ 在
def is_at(messageRaw:str):
    if re.compile(at_pattern).search(messageRaw): return True
    return False

# 语句输入
def inputStatement(message:GroupMessage|PrivateMessage):
    text = f"QQ号 {message.user_id} 用户 {message.sender.nickname} 对你说话："
    clean_msg = re.sub(at_pattern,'', message.raw_message).strip()
    text += clean_msg
    return text

# 获取今天指定时间的时间戳
def get_today_timestamp(hour:int,minute=0,second=0):
    today = datetime.datetime.today()
    specified_time = datetime.time(hour,minute,second)
    specified_datetime = datetime.datetime.combine(today,specified_time)
    return specified_datetime.timestamp()

# 获取监听的群聊
def get_listening_groups(): return config_manager.bot_config.listen_qq_groups

# 获取管理员账号列表
def get_admin_list(): return config_manager.bot_config.admin_list

# 是否同一天
def isEquelDate(date1:datetime.date,date2=datetime.date):
    if date1.month==date2.month and date1.day==date2.day: return True
    else: return False

# 刷新定时器
def updateScheduler(bot:BotClient):
    # 清空任务
    config_manager.scheduler.clear_tasks()
    # 每日执行一次
    # TODO 存在固定代码 尝试分开此处的逻辑
    async def schedule_oneday(bot:BotClient):
        # 日期提醒
        # TODO 临近日期
        dateRemindResult :list = get_dates() # type: ignore
        today = datetime.date.today()
        dateList = []
        remindText = f"==={today.month}月{today.day}日 特别日期===\n"
        if dateRemindResult:
            for obj in dateRemindResult:
                theDate = obj['date']
                if isEquelDate(today,theDate): # type: ignore
                    dateList.append({
                        'date':obj['date'],
                        'title':obj['title'],
                    })
        if len(dateList)>0:
            for obj in dateList:
                remindText += f"{obj['title']}\n"
            for groupId in get_listening_groups():
                await bot.api.post_group_msg(group_id=groupId,text=remindText)
    config_manager.scheduler.schedule_task(
        lambda: asyncio.create_task(schedule_oneday(bot)),
        60*60*24,
        True,
        get_today_timestamp(hour=10)
    )
    # 处理定时消息
    # TODO ERROR 工作异常 
    sql = "SELECT * FROM schedule_messages"
    results = config_manager.mysql_connector.query_data(sql)
    if results:
        for item in results:
            schedule_time = datetime.datetime.strptime(str(item['time']),'%Y-%m-%d %H:%M:%S')
            message_text = item['message']
            group_id = int(item['groupid'])
            if item['isloop']==1:
                def create_loop_task():
                    async def loop_wrapper():
                        await bot.api.post_group_msg(
                            group_id=group_id,
                            text=message_text
                        )
                    return loop_wrapper
                # 计算首次执行时间
                now = datetime.datetime.now()
                initial_delay = (schedule_time-now).total_seconds()
                if initial_delay < 0:
                    loop_seconds = float(item['looptime'])
                    initial_delay = loop_seconds - (abs(initial_delay)%loop_seconds)
                config_manager.scheduler.schedule_task(
                    create_loop_task(),
                    float(item['looptime']),
                    True,
                    time.time()+initial_delay
                )
            else:
                def create_one_time_task():
                    async def one_time_wrapper():
                        await bot.api.post_group_msg(
                            group_id=group_id,
                            text=message_text
                        )
                        config_manager.mysql_connector.execute_query(
                            "DELETE FROM schedule_messages WHERE Id = %s",
                            (item['Id'],)
                        )
                    return one_time_wrapper
                delay = (schedule_time - datetime.datetime.now()).total_seconds()
                if delay>0:
                    config_manager.scheduler.schedule_task(
                        create_one_time_task(),
                        delay,
                        False
                    )
                else:
                    config_manager.mysql_connector.execute_query(
                        "DELETE FROM schedule_messages WHERE Id = %s",
                        (item['Id'],)
                    )
