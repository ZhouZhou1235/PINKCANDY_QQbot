# 设置功能

from ncatbot.core import GroupMessage
from ncatbot.core import BotClient
from core.napcat_api import *
from core.data_models import *
from core.global_utils import *
from core.config_manager import config_manager


# 在群聊中设置功能
async def group_setting_action(bot:BotClient,message:GroupMessage):
    if message.group_id in config_manager.bot_config.listen_qq_groups and message.user_id in config_manager.bot_config.admin_list:
        messageContent = message.raw_message
        if messageContent==getCommendString("clear_memories"):
            config_manager.chat_robot.clear_memories()
            message.reply_sync(text="PINKCANDY: clear memories done!")
        # TODO 设置日期提醒
