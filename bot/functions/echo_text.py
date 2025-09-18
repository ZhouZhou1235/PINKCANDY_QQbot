# 机器回复文本

import platform
import random
import psutil
import requests
import asyncio
from ncatbot.core import GroupMessage
from ncatbot.core import BotClient
from core.napcat_api import *
from core.data_models import *
from core.global_utils import *
from core.config_manager import config_manager
from functions.share_functions import *


# 群聊回应文字内容
@eventCoolDown(5)
async def group_echo_text(bot:BotClient,message:GroupMessage):
    if message.group_id not in config_manager.bot_config.listen_qq_groups: return
    messageContent = message.raw_message
    groupId = message.group_id
    # 帮助
    if messageContent==getCommendString("help"):
        help_text = config_manager.bot_config.bot_name
        help_text += "\n"
        help_text += config_manager.bot_config.bot_info
        help_text += "\n"
        commends = config_manager.bot_config.function_command_info
        for info in commends:
            help_text += f"{info}\n"
        bot.api.post_group_msg_sync(group_id=groupId,text=help_text)
    # 测试
    elif messageContent==getCommendString("test"):
        gallery_system_web = "https://gallery-system.pinkcandy.top"
        try:
            replyText = "===\n机器运行测试\n===\n"
            replyText += f"{platform.uname().node} {platform.uname().system} {platform.uname().release}\n"
            replyText += f"CPU-{psutil.cpu_percent(interval=1)}% 内存-{psutil.virtual_memory().percent}%\n"
            replyText += f"粉糖画廊接口 {requests.post(gallery_system_web).text}"
            bot.api.post_group_msg_sync(group_id=groupId,text=replyText)
        except Exception as e:
            print(e)
            await message.reply(text=f"PINKCANDY ERROR:{e}")
    # 抽群友
    elif messageContent.find(getCommendString("random_get_member"))!=-1:
        command = getCommendString("random_get_member")
        try:
            memberList = api_getGroupMembers(bot,message.group_id)
            if messageContent == command:
                theMember = random.choice(memberList)
                echo_text = f"抽到 {theMember.nickname}\n"
                echo_text += f"[CQ:image,summary=[{theMember.nickname}],url=http://q.qlogo.cn/headimg_dl?dst_uin={theMember.user_id}&spec=640&img_type=jpg]\n"
                await message.reply(text=echo_text)
            else:
                numstr = messageContent[len(command)+1:].replace(' ','')
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
    # 列出特别日期
    elif messageContent==getCommendString("list_dates"):
        dateRemindResult :list = get_dates() # type: ignore
        dateList = []
        remindText = f"===特别日期===\n"
        if dateRemindResult:
            for obj in dateRemindResult:
                dateList.append({
                    'date':obj['date'],
                    'title':obj['title'],
                })
        if len(dateList)>0:
            for obj in dateList:
                theDate :datetime.date = obj['date']
                if message.group_id in config_manager.bot_config.full_show_groups:
                    remindText += f"{theDate.month}月{theDate.day}日 - {obj['title']}\n"
                else:
                    remindText += f"{theDate.month}月{theDate.day}日 - ......\n"
        result = await bot.api.post_group_msg(group_id=groupId,text=remindText)
        # 不完全展示的群一分钟后撤回
        if message.group_id not in config_manager.bot_config.full_show_groups:
            message_id = result['data']['message_id']
            async def delete_after_delay():
                await asyncio.sleep(10)
                await bot.api.delete_msg(message_id=message_id)
            asyncio.create_task(delete_after_delay())

    # 临近日期提醒
    elif messageContent==getCommendString("remind_neardate"):
        await remind_neardate(bot,groupId)
    # 概率触发
    else:
        # 跟着说话
        if random.randint(0,199)<1:
            try:
                session_id = str(groupId)
                theMessageList:list = await api_getGroupMessageHistory(bot,groupId,25)
                if theMessageList:
                    messagesString = ""
                    for m in theMessageList:
                        messagesString += f"[id{m['sender']['user_id']} nickname{m['sender']['user_id']}:{m['raw_message']}]"
                    auto_input = f"""
                        {messagesString}
                        根据上面的聊天跟着说句话，不要发负面内容。不宜超过25字。
                    """
                    response = await config_manager.chat_robot.group_chat(session_id,auto_input)
                    await bot.api.post_group_msg(group_id=groupId, text=str(response))
            except Exception as e: print(e)
        # 戳发送者
        elif random.randint(0,149)<1:
            bot.api.send_poke_sync(user_id=message.user_id,group_id=groupId)
