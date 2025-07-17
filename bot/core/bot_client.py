# 机器客户端

import asyncio
from typing import Any,Callable
from functions.echo_text import *
from core.bot_config import Config
from ncatbot.core import BotClient
from ncatbot.utils import get_log

class QQbot:
    def __init__(self):
        self.bot_config = Config() # 配置
        self.bot_log = get_log() # 聊天记录器
        self.bot_client = BotClient() # ncatbot客户端
    # 添加群聊消息监听事件
    def add_group_event(self,handler:Callable[...,Any],*args,**kwargs):
        bot_client = self.bot_client
        log = self.bot_log
        @bot_client.group_event()
        async def on_group_message(message:GroupMessage):
            try:
                log.info(f"[group message] {message}")
                if asyncio.iscoroutinefunction(handler):await handler(message,*args,**kwargs)
                else:handler(message,*args,**kwargs)
            except Exception as e:log.error(f"PINKCANDY ERROR:{e}")
    # 添加私聊消息监听事件
    def add_private_event(self,handler:Callable[...,Any],*args,**kwargs):
        bot_client = self.bot_client
        log = self.bot_log
        @bot_client.private_event()
        async def on_private_message(message:PrivateMessage):
            try:
                log.info(f"[private message] {message}")
                if asyncio.iscoroutinefunction(handler):await handler(message,*args,**kwargs)
                else:handler(message,*args,**kwargs)
            except Exception as e:log.error(f"PINKCANDY ERROR:{e}")
    # 添加事件
    def add_talk_events(self):
        self.add_group_event(self.bot_client,hello_everyone)
        self.add_private_event(self.bot_client,hello_user)
        # ...
    # 运行
    def bot_run(self):
        self.add_talk_events()
        self.bot_client.run(bt_uin=self.bot_config.qq_number)
