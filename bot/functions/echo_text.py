# 机器回复文本
from ncatbot.core import GroupMessage,PrivateMessage
from ncatbot.core import BotClient

# 群聊问好
def hello_everyone(message:GroupMessage):
    if message.raw_message == "粉糖终端"or"PINKCANDY QQ Machine":
        message.reply(text="我是由生灵小蓝狗制造的粉糖终端")

# 私聊问好
def hello_user(bot:BotClient,message:PrivateMessage):
    if message.raw_message == "粉糖终端"or"PINKCANDY QQ Machine":
        bot.api.post_private_msg(
            message.user_id,
            text=f"{message.sender.nickname}，我是由生灵小蓝狗制造的粉糖终端。"
        )
