# 机器回复文本

import platform
import random
import ncatbot
from ncatbot.core import GroupMessage
from ncatbot.core import BotClient
import requests
from core.napcat_api import *
from core.data_models import *
from core.global_utils import *
from core.config_manager import config_manager


# 群聊回应文字内容
@eventCoolDown(5)
async def group_echo_text(bot:BotClient,message:GroupMessage):
    if message.group_id not in config_manager.bot_config.listen_qq_groups: return
    messageContent = message.raw_message
    groupId = message.group_id
    if messageContent==getCommendString("help"):
        help_text = config_manager.bot_config.bot_name
        help_text += "\n"
        help_text += config_manager.bot_config.bot_info
        help_text += "\n"
        commends = config_manager.bot_config.function_command_info
        for info in commends:
            help_text += f"{info}\n"
        bot.api.post_group_msg_sync(group_id=groupId,text=help_text)
    elif messageContent==getCommendString("test"):
        try:
            replyText = "===\n机器运行测试\n===\n"
            replyText += f"载体计算机 {platform.uname().node} {platform.uname().system} {platform.uname().release}\n"
            replyText += f"python解释器 {platform.python_version()}\n"
            replyText += f"机器框架 {ncatbot.__name__} {ncatbot.__version__} 与 NapCat\n"
            replyText += f"与幻想动物画廊通信...... {requests.post(config_manager.bot_config.GALLERY_SYSTEM_WEB).text}"
            bot.api.post_group_msg_sync(group_id=groupId,text=replyText)
        except Exception as e:
            print(e)
            await message.reply(text=f"PINKCANDY ERROR:{e}")
    elif messageContent==getCommendString("random_get_member") or messageContent[:len(getCommendString("random_get_member"))]==getCommendString("random_get_member"):
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
