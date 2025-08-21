# 设置功能

import re
import datetime
from ncatbot.core import GroupMessage
from ncatbot.core import BotClient
from core.napcat_api import *
from core.data_models import *
from core.global_utils import *
from core.config_manager import config_manager
from functions.share_functions import *


# 在群聊中设置功能
async def group_setting_action(bot:BotClient,message:GroupMessage):
    messageContent = message.raw_message
    if message.group_id in get_listening_groups():
        # 仅管理员
        if message.user_id in get_admin_list():
            if messageContent==getCommendString("clear_memories"):
                config_manager.chat_robot.clear_memories()
                config_manager.mysql_connector.execute_query("TRUNCATE group_chat_memories")
                config_manager.mysql_connector.execute_query("TRUNCATE private_chat_memories")
                message.reply_sync(text="PINKCANDY: clear memories done!")
            # 删除特别日期
            elif messageContent.find(getCommendString("delete_date"))!=-1:
                try:
                    pattern = r'(\d{1,2})\.(\d{1,2})'
                    a_match = re.search(pattern,messageContent)
                    if a_match:
                        month = int(a_match.group(1))
                        day = int(a_match.group(2))
                        date = datetime.date(year=datetime.datetime.today().year,month=month,day=day)
                        done = config_manager.mysql_connector.execute_query(f"DELETE FROM date_reminder WHERE date='{date}'")
                        if done:
                            await message.reply(text="PINKCANDY: delete date ok.")
                        else:
                            await message.reply(text="PINKCANDY ERROR: delete date failed.")
                except Exception as e: print(e)
        # 列出管理员
        if messageContent==getCommendString("list_admin"):
            text = "===管理员===\n"
            for admin_userId in get_admin_list():
                res = await api_getUser(bot,admin_userId)
                text += f"{res['data']['nick']}\n"
            await bot.api.post_group_msg(group_id=message.group_id,text=text)
        # 列出服务的群聊
        if messageContent==getCommendString("list_groups"):
            text = "===服务群聊===\n"
            for groupId in get_listening_groups():
                res = await api_getGroups(bot,groupId)
                print(res)
                text += f"{res['data']['group_name']}\n"
            await bot.api.post_group_msg(group_id=message.group_id,text=text)
        # 添加特别日期
        elif messageContent.find(getCommendString("add_date"))!=-1:
            try:
                pattern = r'(\d{1,2})\.(\d{1,2})\s*([^\s]+)'
                a_match = re.search(pattern,messageContent)
                if a_match:
                    month = int(a_match.group(1))
                    day = int(a_match.group(2))
                    title = a_match.group(3)
                    date = datetime.date(year=datetime.datetime.today().year,month=month,day=day)
                    done = config_manager.mysql_connector.execute_query(f"INSERT INTO date_reminder VALUES('{title}','{date}')")
                    if done:
                        await message.reply(text="PINKCANDY: add date ok.")
                    else:
                        await message.reply(text="PINKCANDY ERROR: add date failed.")
            except Exception as e: print(e)
        # 添加一次定时
        elif messageContent.find(getCommendString("add_schedule")) != -1:
            await add_schedule_task(bot,message,False)
        # 添加重复定时
        elif messageContent.find(getCommendString("add_loop_schedule")) != -1:
            await add_schedule_task(bot,message,True)
        # 取消定时
        elif messageContent.find(getCommendString("delete_schedule")) != -1:
            await delete_schedule_task(bot, message)
        # 列出定时任务
        elif messageContent == getCommendString("list_schedule"):
            await list_schedule_tasks(bot, message)
