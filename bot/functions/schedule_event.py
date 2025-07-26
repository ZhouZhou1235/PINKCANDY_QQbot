# 定时执行事件

from core.config_manager import config_manager
from ncatbot.core import BotClient

# 终端聊天总结
async def group_chat_summary(bot: BotClient):
    for groupId in config_manager.bot_config.listen_qq_groups:
        try:
            session_id = str(groupId)
            auto_input = """
                创造者要求你总结你与本群所有用户对话的聊天内容
                使用这样的格式：
                    今天的对话提到 a b c......
                    来自粉糖终端的总结
            """
            response = await config_manager.chat_robot.group_chat(session_id,auto_input)
            await bot.api.post_group_msg(group_id=groupId, text=str(response))
        except Exception as e: print(e)
