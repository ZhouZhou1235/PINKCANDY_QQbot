# 机器启动器

from typing import Any,Callable
from functions.schedule_event import *
from functions.chat_with_robot import *
from functions.echo_text import *
from functions.echo_media import *
from functions.setting_action import *
from ncatbot.core import BotClient,GroupMessage,PrivateMessage
from ncatbot.utils import get_log
import asyncio
import datetime


# 向机器添加消息监听事件
def add_listen_event(bot_client:BotClient,handler:Callable[...,Any],isGroup:bool=True,*args,**kwargs):
    log = get_log()
    async def wrapped_handler(message):
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(bot_client,message,*args,**kwargs)
            else:
                handler(bot_client,message,*args,**kwargs)
        except Exception as e:
            log.error(f"PINKCANDY ERROR:{e}")
    if isGroup:
        @bot_client.group_event()
        async def on_group_message(message:GroupMessage):
            log.info(f"[group message] {message}")
            await wrapped_handler(message)
    else:
        @bot_client.private_event()
        async def on_private_message(message:PrivateMessage):
            log.info(f"[private message] {message}")
            await wrapped_handler(message)

# 为客户端注册默认事件
def add_default_event_to_bot(bot:BotClient):
    add_listen_event(bot,group_echo_text)
    add_listen_event(bot,group_echo_media)
    add_listen_event(bot,group_chat_with_robot)
    add_listen_event(bot,group_setting_action)
    add_listen_event(bot,private_chat_with_robot,False)

# 开始时设置定时任务
def begin_add_schedule(bot:BotClient):
    # 计算首次执行的延迟时间（秒）
    def calculate_first_delay(target_hour:int,target_minute=0,target_second=0):
        now = datetime.datetime.now()
        target_time_today = datetime.datetime(now.year, now.month, now.day, target_hour, target_minute, target_second)
        delay_seconds = 0
        if now < target_time_today:
            delay_seconds = (target_time_today - now).total_seconds()
        else:
            target_time_tomorrow = target_time_today + datetime.timedelta(days=1)
            delay_seconds = (target_time_tomorrow - now).total_seconds()
        return int(delay_seconds)
    # 每日任务
    async def run_and_loop_daily():
        await schedule_oneday(bot)
        config_manager.date_scheduler.schedule_loop_task(
            60 * 60 * 24,
            schedule_oneday,
            bot
        )
    daily_delay = calculate_first_delay(10,0,0)
    config_manager.date_scheduler.schedule_task(
        daily_delay,
        run_and_loop_daily
    )
    # 每三天任务  
    async def run_and_loop_threeday():
        await schedule_threeday(bot)
        config_manager.date_scheduler.schedule_loop_task(
            60 * 60 * 24 * 3,
            schedule_threeday,
            bot
        )
    three_day_delay = calculate_first_delay(11, 0, 0)
    config_manager.date_scheduler.schedule_task(
        three_day_delay,
        run_and_loop_threeday
    )
    # 每周任务
    async def run_and_loop_weekly():
        await schedule_week(bot)
        config_manager.date_scheduler.schedule_loop_task(
            60 * 60 * 24 * 7,
            schedule_week,
            bot
        )
    weekly_delay = calculate_first_delay(12, 0, 0)
    config_manager.date_scheduler.schedule_task(
        weekly_delay,
        run_and_loop_weekly
    )
    updateMessageScheduler(bot)

# 创建客户端
def create_bot(): 
    bot = BotClient()
    add_default_event_to_bot(bot)
    begin_add_schedule(bot)
    return bot
