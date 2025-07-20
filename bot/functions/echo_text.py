# 机器回复文本

import platform
import random
import ncatbot
from ncatbot.core import GroupMessage,PrivateMessage
from ncatbot.core import BotClient
import requests
from core.napcat_api import *
from core.data_models import *
from GArea import *


# === 群聊

# 问好
async def hi_everyone(message:GroupMessage):
    if message.group_id in g_bot_config.listen_qq_groups:
        if message.raw_message == getCommendString("hi"):
            await message.reply(text="我是由生灵小蓝狗制造的粉糖终端")

# 帮助
async def print_help(message:GroupMessage):
    if message.group_id in g_bot_config.listen_qq_groups:
        if message.raw_message == getCommendString("help"):
            help_text = g_bot_config.bot_name
            help_text += "\n"
            help_text += g_bot_config.bot_info
            help_text += "\n"
            commends = g_bot_config.function_command_info
            for info in commends:
                help_text += f"{info}\n"
            await message.reply(text=help_text)

# 测试
async def run_print_test(message:GroupMessage):
    if message.group_id in g_bot_config.listen_qq_groups:
        if message.raw_message == getCommendString("test"):
            try:
                replyText = "\n===\n机器运行测试\n===\n"
                replyText += f"载体计算机 {platform.uname().node} {platform.uname().system} {platform.uname().release}\n"
                replyText += f"python解释器 {platform.python_version()}\n"
                replyText += f"机器框架 {ncatbot.__name__} {ncatbot.__version__} 与 NapCat\n"
                replyText += f"与幻想动物画廊通信...... {requests.post(GALLERY_SYSTEM_WEB).text}"
                await message.reply(text=replyText)
            except Exception as e:
                print(e)
                await message.reply(text=f"PINKCANDY ERROR:{e}")

# 随机选群友
async def random_get_member(message:GroupMessage,bot:BotClient):
    if message.group_id in g_bot_config.listen_qq_groups:
        command = getCommendString("random_get_member")
        try:
            memberList = api_getGroupMembers(bot,message.group_id)
            if message.raw_message == command:
                theMember = random.choice(memberList)
                echo_text = f"抽到 {theMember.nickname}\n"
                echo_text += f"[CQ:image,summary=[{theMember.nickname}],url=http://q.qlogo.cn/headimg_dl?dst_uin={theMember.user_id}&spec=640&img_type=jpg]\n"
                await message.reply(text=echo_text)
            elif message.raw_message[:len(command)] == command:
                numstr = message.raw_message[len(command):].replace(' ','')
                num = int(numstr)
                if num<0 or num>5 or num>len(memberList):
                    await message.reply("PINKCANDY: num error")
                else:
                    theMembers :List[GroupMember] = randomGetListElements(memberList,num) # type: ignore
                    if theMembers:
                        echo_text = "连抽群友\n"
                        for theMember in theMembers:
                            echo_text += f"{theMember.nickname}"
                            echo_text += f"[CQ:image,summary=[{theMember.nickname}],url=http://q.qlogo.cn/headimg_dl?dst_uin={theMember.user_id}&spec=640&img_type=jpg]"
                            echo_text += "\n"
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
