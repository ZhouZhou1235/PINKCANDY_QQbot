# NapCat QQ协议接口

from typing import List
from ncatbot.core import BotClient
from core.data_models import *

# 获取群聊成员列表
def api_getGroupMembers(bot:BotClient,groupId:int):
    result = bot.api.get_group_member_list_sync(group_id=groupId)
    members :List[GroupMember] = [GroupMember.load(obj) for obj in result['data']]
    return members
