# 与人工智能体对话

import re
from ncatbot.core import GroupMessage
from ncatbot.core import BotClient
from core.napcat_api import *
from core.data_models import *
from core.global_utils import *
from core.config_manager import config_manager

# 语句输入
def inputStatement(message:GroupMessage):
    text = f"QQ号 {message.user_id} 用户 {message.sender.nickname} 对你说话："
    clean_msg = re.sub(
        rf'\[CQ:at,qq={config_manager.bot_config.qq_number}\]|@{config_manager.bot_config.bot_name}',
        '', 
        message.raw_message
    ).strip()
    text += clean_msg
    return text

# 在群聊中与机器对话
async def group_chat_with_robot(bot:BotClient,message:GroupMessage):
    if message.group_id not in config_manager.bot_config.listen_qq_groups: return
    if not re.compile(rf'\[CQ:at,qq={config_manager.bot_config.qq_number}\]').search(message.raw_message): return
    try:
        session_id = f"qq_{message.sender.user_id}"
        response = await config_manager.chat_robot.chat(session_id,inputStatement(message))
        bot.api.post_group_msg_sync(group_id=message.group_id,text=str(response))
    except Exception as e: print(f"PINKCANDY ERROR: {e.__context__}")
