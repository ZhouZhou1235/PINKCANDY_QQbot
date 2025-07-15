# 启动

# ncatbot机器人 最简示例
# from ncatbot.core import BotClient, GroupMessage, PrivateMessage
# from ncatbot.utils import get_log
# bot = BotClient()
# _log = get_log()
# @bot.group_event()
# async def on_group_message(msg: GroupMessage):
#     _log.info(msg)
#     if msg.raw_message == "test":
#         await msg.reply(text="PINKCANDY: group test ok")
# @bot.private_event()
# async def on_private_message(msg: PrivateMessage):
#     _log.info(msg)
#     if msg.raw_message == "test":
#         await bot.api.post_private_msg(msg.user_id, text="PINKCANDY: test ok")
# bot.run(bt_uin="qq number")

