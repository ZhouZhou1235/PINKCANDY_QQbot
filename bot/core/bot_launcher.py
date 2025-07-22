# 机器启动器

import asyncio
from typing import Any,Callable
from functions.echo_text import *
from functions.echo_media import *
from ncatbot.core import BotClient
from ncatbot.utils import get_log

# 向机器添加消息监听事件
def add_listen_event(bot_client:BotClient,handler:Callable[...,Any],isGroup:bool=True,*args,**kwargs):
    log = get_log()
    async def wrapped_handler(message):
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(message,*args,**kwargs)
            else:
                handler(message,*args,**kwargs)
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

    # TODO 解决报错 missing 1 required positional argument: 'message'

    bot = BotClient()
    add_listen_event(bot,hi_everyone)
    add_listen_event(bot,print_help)
    add_listen_event(bot,run_print_test)
    add_listen_event(bot,random_get_member)
    add_listen_event(bot,get_gallery_artwork)
    add_listen_event(bot,chat_with_robot)
    add_listen_event(bot,hi_user,False)
    return bot
