# 添加QQ机器监听事件
# TODO 将添加监听事件的行为封装

from ncatbot.core import GroupMessage,PrivateMessage
from QQBot import QQbot

# 添加一条群聊监听事件
def add_group_event(qqbot:QQbot,f:function):
    botClient = qqbot.bot_client
    log = qqbot.bot_log
    @botClient.group_event()
    async def on_group_message(message:GroupMessage):
        log.info(message)
        function.__call__(f,qqbot,message)

# 添加一条私聊监听事件
def add_private_event(qqbot:QQbot,f:function):
    botClient = qqbot.bot_client
    log = qqbot.bot_log
    @botClient.private_event()
    async def on_private_message(message:PrivateMessage):
        log.info(message)
        function.__call__(f,qqbot,message)
