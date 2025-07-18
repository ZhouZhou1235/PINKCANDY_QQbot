# 机器回复文本
import platform
import random
import ncatbot
from ncatbot.core import GroupMessage,PrivateMessage
from ncatbot.core import BotClient
from core.napcat_api import *
from core.data_models import *
from core.bot_config import Config

bot_config = Config()

# 得到指令对应的文本
def getCommendString(commendKey:str):
    return f"{bot_config.fixed_begin} {bot_config.function_commands[commendKey]}"


# === 群聊

# 问好
async def hi_everyone(message:GroupMessage):
    if message.group_id in bot_config.listen_qq_groups:
        if message.raw_message == getCommendString("hi"):
            await message.reply(text="我是由生灵小蓝狗制造的粉糖终端")

# 帮助
async def print_help(message:GroupMessage):
    if message.group_id in bot_config.listen_qq_groups:
        if message.raw_message == getCommendString("help"):
            help_text = bot_config.bot_name
            help_text += "\n"
            help_text += bot_config.bot_info
            help_text += "\n"
            commends = bot_config.function_commands
            for key in commends.keys():
                help_text += f"{commends[key]}\n"
            await message.reply(text=help_text)

# 测试
async def run_print_test(message:GroupMessage):
    if message.group_id in bot_config.listen_qq_groups:
        if message.raw_message == getCommendString("test"):
            replyText = "\n===\n机器运行测试\n===\n"
            replyText += f"载体计算机 {platform.uname().node} {platform.uname().system} {platform.uname().release}\n"
            replyText += f"python解释器 {platform.python_version()}\n"
            replyText += f"机器框架 {ncatbot.__name__} {ncatbot.__version__} 与 NapCat\n"
            replyText += f"机器工作正常" 
            await message.reply(text=replyText)

# 随机选群友
async def random_get_member(message:GroupMessage,bot:BotClient):
    if message.group_id in bot_config.listen_qq_groups:
        if message.raw_message == getCommendString("random_get_member"):
            try:
                memberList = api_getGroupMembers(bot,message.group_id)
                theMember = random.choice(memberList)
                echo_text = f"{message.sender.nickname}抽到了{theMember.nickname}"
                await message.reply(text=echo_text)
            except Exception as e: print(f"PINKCANDY ERROR:{e}")


# === 私聊

# 问好
async def hi_user(message:PrivateMessage,bot:BotClient):
    if message.raw_message == getCommendString("hi"):
        await bot.api.post_private_msg(
            message.user_id,
            text=f"{message.sender.nickname}，我是由生灵小蓝狗制造的粉糖终端。"
        )

