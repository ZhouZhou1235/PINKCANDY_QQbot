# NapCat QQ协议接口

import json
from typing import List
from ncatbot.core import BotClient
from core.data_models import *

# 获取群聊成员列表
def api_getGroupMembers(bot:BotClient,groupId:int):
    result = bot.api.get_group_member_list_sync(group_id=groupId)
    members :List[GroupMember] = [GroupMember.load(obj) for obj in result['data']]
    return members

# 获取群聊聊天历史记录
async def api_getGroupMessageHistory(bot:BotClient,groupId:int|str,count:int):
    result = await bot.api.get_group_msg_history(
        group_id=groupId,
        message_seq=0,
        count=count,
        reverse_order=False
    )
    theMessageList:list = json.loads(str(result).replace("'","\""))['data']['messages']
    return theMessageList

# 获取群友信息
async def api_getGroupMember(bot:BotClient,groupId:int|str,userId:int|str):
    member :GroupMember = await bot.api.get_group_member_info(
        group_id=groupId,
        user_id=userId,
        no_cache=True
    )
    return member

# 获取qq用户信息
async def api_getUser(bot:BotClient,userId:int|str):
    res = await bot.api.get_stranger_info(user_id=userId)
    return res

# 获取qq群聊信息
async def api_getGroups(bot:BotClient,groupId:int|str):
    res = await bot.api.get_group_info(group_id=groupId)
    return res
