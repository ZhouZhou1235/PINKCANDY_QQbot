# 设置功能

from ncatbot.core import GroupMessage
from ncatbot.core import BotClient
from core.napcat_api import *
from core.data_models import *
from core.global_utils import *
from core.config_manager import config_manager
import re
import datetime


# 在群聊中设置功能
async def group_setting_action(bot:BotClient,message:GroupMessage):
    messageContent = message.raw_message
    if message.group_id in get_listening_groups():
        # 仅管理员
        if message.user_id in get_admin_list():
            # 抹除记忆
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
        # 添加一次定时说话
        elif messageContent.find(getCommendString("add_schedule"))!=-1:
            try:
                parts = messageContent.split()
                if len(parts)>=4:
                    delay_minutes = int(parts[2])
                    message_text = ' '.join(parts[3:])
                    schedule_time = datetime.datetime.now() + datetime.timedelta(minutes=delay_minutes)
                    sql = """
                        INSERT INTO schedule_messages 
                        (time, message, groupid, isloop, looptime) 
                        VALUES (%s,%s,%s,%s,%s)
                    """
                    params = (
                        schedule_time.strftime('%Y-%m-%d %H:%M:%S'),
                        message_text,
                        str(message.group_id),
                        0,
                        0
                    )
                    if config_manager.mysql_connector.execute_query(sql,params):
                        await message.reply(f"PINKCANDY: add schedule done.")
                        updateScheduler(bot)
                    else:
                        await message.reply("PINKCANDY ERROR: add schedule failed!")
                else:
                    await message.reply("PINKCANDY ERROR: format error.")
            except Exception as e: print(e)
        # 添加重复定时说话
        elif messageContent.find(getCommendString("add_loop_schedule"))!=-1:
            try:
                parts = messageContent.split()
                if len(parts)>=5:
                    start_time = parts[2]
                    loop_minutes = int(parts[3])
                    message_text = ' '.join(parts[4:])
                    hour, minute = map(int, start_time.split(':'))
                    now = datetime.datetime.now()
                    schedule_time = datetime.datetime(now.year, now.month, now.day, hour, minute)
                    sql = """
                        INSERT INTO schedule_messages 
                        (time, message, groupid, isloop, looptime) 
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    params = (
                        schedule_time.strftime('%Y-%m-%d %H:%M:%S'),
                        message_text,
                        str(message.group_id),
                        1,
                        loop_minutes*60
                    )
                    if config_manager.mysql_connector.execute_query(sql, params):
                        await message.reply(f"PINKCANDY: add loop schedule done.")
                        updateScheduler(bot)
                    else:
                        await message.reply("PINKCANDY ERROR: add loop schedule failed!")
                else:
                    await message.reply("PINKCANDY ERROR: format error.")
            except Exception as e: print(e)
        # 取消定时说话
        elif messageContent.find(getCommendString("delete_schedule"))!=-1:
            try:
                parts = messageContent.split()
                if len(parts)>=3:
                    schedule_id = parts[2]
                    sql = "DELETE FROM schedule_messages WHERE Id = %s"
                    if config_manager.mysql_connector.execute_query(sql, (schedule_id,)):
                        await message.reply(f"PINKCANDY: delete schedule done.")
                        updateScheduler(bot)
                    else:
                        await message.reply("PINKCANDY ERROR: delete schedule failed!")
                else:
                    await message.reply("PINKCANDY ERROR: format error.")
            except Exception as e:  print(e)
        # 列出定时说话
        elif messageContent.find(getCommendString("list_schedule"))!=-1:
            try:
                sql = """
                    SELECT * FROM schedule_messages 
                    ORDER BY isloop DESC,time ASC
                """
                results = config_manager.mysql_connector.query_data(sql)
                if results:
                    text = "===定时说话===\n"
                    for item in results:
                        schedule_time = datetime.datetime.strptime(str(item['time']),'%Y-%m-%d %H:%M:%S')
                        if item['isloop']:
                            text += f"[号码{item['Id']}] 每{item['looptime']//60}分钟发 {item['message'][:10]}...\n"
                        else:
                            text += f"[号码{item['Id']}] {schedule_time.strftime('%m-%d %H:%M')}发 {item['message'][:10]}...\n"
                    await message.reply(text)
                else:
                    await message.reply("PINKCANDY: empty schedule.")
            except Exception as e: print(e)
