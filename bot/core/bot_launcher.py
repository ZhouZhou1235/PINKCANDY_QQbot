# 机器启动器

import asyncio
from typing import Any,Callable
from functions.chat_with_robot import *
from functions.echo_text import *
from functions.echo_media import *
from ncatbot.core import BotClient,GroupMessage,PrivateMessage
from ncatbot.utils import get_log

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

# 创建机器客户端
def create_bot():
    bot = BotClient()
    # 注册事件 默认群聊
    add_listen_event(bot,group_echo_text)
    add_listen_event(bot,group_echo_media)
    add_listen_event(bot,group_chat_with_robot)
    # 私聊
    add_listen_event(bot,private_chat_with_robot,False)
    return bot
