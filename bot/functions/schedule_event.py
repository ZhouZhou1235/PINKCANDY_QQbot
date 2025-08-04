# 定时执行事件

from core.config_manager import config_manager
from ncatbot.core import BotClient
from core.napcat_api import api_getGroupMessageHistory


# 终端聊天总结
async def group_chat_summary(bot: BotClient):
    for groupId in config_manager.bot_config.listen_qq_groups:
        try:
            session_id = str(groupId)
            result = await bot.api.get_group_msg_history(
                group_id=groupId,
                message_seq=0,
                count=3,
                reverse_order=False
            )
            theMessageList:list = await api_getGroupMessageHistory(bot,groupId,100)
            if theMessageList:
                messagesString = ""
                for m in theMessageList:
                    messagesString += f"[id{m['sender']['user_id']} nickname{m['sender']['user_id']}:{m['raw_message']}]"
                auto_input = f"""
                    {messagesString}
                    简单评价以上对话聊天内容,不宜超过100字。
                """
                response = await config_manager.chat_robot.group_chat(session_id,auto_input)
                await bot.api.post_group_msg(group_id=groupId, text=str(response))
        except Exception as e: print(e)
