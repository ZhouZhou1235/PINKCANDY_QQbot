# 共用的函数

import re
import time
import datetime
from ncatbot.core import BotClient
from core.config_manager import config_manager
from ncatbot.core import GroupMessage
from core.global_utils import *


# 查询特别日期
def get_dates(): return config_manager.mysql_connector.query_data("SELECT * FROM date_reminder")

# 载入定时说话
def load_scheduled_messages(bot: BotClient):
    try:
        config_manager.mysql_connector.execute_query("DELETE FROM schedule_messages WHERE time<NOW() and isloop=0")
        config_manager.message_scheduler.clear_all_tasks()
        result = config_manager.mysql_connector.query_data("SELECT * FROM schedule_messages")
        if result:
            print(result)
            for obj in result:
                time :datetime.datetime = obj['time']
                groupid = obj['groupid']
                content = obj['message']
                is_loop = int(obj['isloop'])==1
                interval_seconds = int(obj['looptime'])
                start_timestamp = time.timestamp()
                def send_scheduled_message(bot:BotClient,group_id:int,message_content:str):
                    bot.api.post_group_msg_sync(group_id=group_id,text=message_content)
                config_manager.message_scheduler.schedule_task(
                    send_scheduled_message,
                    interval_seconds if is_loop else 0,
                    is_loop,
                    start_timestamp,
                    (bot,groupid,content)
                )
    except Exception as e: print(e)

# 添加定时任务
async def add_schedule_task(bot:BotClient,message:GroupMessage,is_loop:bool):
    try:
        command = getCommendString("add_loop_schedule") if is_loop else getCommendString("add_schedule")
        content = message.raw_message[len(command):].strip()
        if is_loop:
            pattern = r'(\d{1,2}:\d{2})\s+(\d+)\s+(.+)'
            match = re.match(pattern, content)
            if not match:
                await message.reply("PINKCANDY: format error.")
                return
            time_str = match.group(1)
            interval_minutes = int(match.group(2))
            message_content = match.group(3)
            hour,minute = map(int, time_str.split(':'))
            today = datetime.datetime.today()
            start_time = datetime.datetime(today.year,today.month,today.day,hour,minute)
            start_timestamp = start_time.timestamp()
            interval_seconds = interval_minutes*60
        else:
            pattern = r'(\d+)\s+(.+)'
            match = re.match(pattern, content)
            if not match:
                await message.reply("PINKCANDY: format error.")
                return
            delay_minutes = int(match.group(1))
            message_content = match.group(2)
            start_timestamp = time.time() + (delay_minutes*60)
            interval_seconds = 0
        sql = """
            INSERT INTO schedule_messages(time,message,groupid,isloop,looptime,addtime)
            VALUES (%s,%s,%s,%s,%s,NOW())
        """
        params = (
            datetime.datetime.fromtimestamp(start_timestamp),
            message_content,
            str(message.group_id),
            1 if is_loop else 0,
            interval_seconds
        )
        result = config_manager.mysql_connector.execute_query(sql,params)
        if result:
            def send_scheduled_message(bot:BotClient,group_id:int,message_content:str):
                bot.api.post_group_msg_sync(group_id=group_id,text=message_content)
            config_manager.message_scheduler.schedule_task(
                send_scheduled_message,
                interval_seconds if is_loop else 0,
                is_loop,
                start_timestamp,
                (bot,message.group_id,message_content)
            )
            await message.reply(f"PINKCANDY: add schedule done.")
        else:
            await message.reply("PINKCANDY: add schedule failed!")
    except Exception as e: print(f"PINKCANDY ERROR: {e}")

# 删除定时任务
async def delete_schedule_task(bot:BotClient,message:GroupMessage):
    try:
        command = getCommendString("delete_schedule")
        task_id_str = message.raw_message[len(command):].strip()
        task_id = int(task_id_str)
        sql = "DELETE FROM schedule_messages WHERE Id = %s"
        result = config_manager.mysql_connector.execute_query(sql,(task_id,))
        if result:
            load_scheduled_messages(bot)
            await message.reply("PINKCANDY: delete schedule done.")
        else:
            await message.reply("PINKCANDY: delete schedule failed!")
            
    except Exception as e: print(f"PINKCANDY ERROR: {e}")

# 列出所有定时任务
async def list_schedule_tasks(bot: BotClient, message: GroupMessage):
    try:
        config_manager.mysql_connector.execute_query("DELETE FROM schedule_messages WHERE time<NOW() and isloop=0")
        sql = f"SELECT * FROM schedule_messages WHERE groupid={message.group_id} ORDER BY isloop,time DESC LIMIT 50"
        results = config_manager.mysql_connector.query_data(sql)
        if not results:
            await message.reply("PINKCANDY: empty schedule.")
            return
        text = "===本群定时说话===\n"
        for task in results: # type: ignore
            task_time = task['time'].strftime("%Y-%m-%d %H:%M") if isinstance(task['time'], datetime.datetime) else str(task['time'])
            task_type = "重复" if task['isloop'] else "一次"
            text += f"{task['Id']} | {task_type} | {task_time}\n"
            text += f"{task['message'][:50]}...\n"
            if task['isloop']:
                text += f"间隔{task['looptime']//60}分钟\n"
            text += "---\n"
        await bot.api.post_group_msg(group_id=message.group_id, text=text)
    except Exception as e: print(f"PINKCANDY ERROR: {e}")
