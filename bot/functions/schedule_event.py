# 定时执行事件

import datetime
from ncatbot.core import BotClient
from functions.share_functions import get_dates
from core.global_utils import get_listening_groups, isEquelDate
from core.config_manager import config_manager

# 每日执行一次
async def schedule_oneday(bot:BotClient):
    # 日期提醒
    dateRemindResult = get_dates()
    today = datetime.date.today()
    dateList = []
    dateNearList = []
    remindText = f"==={today.month}月{today.day}日 特别日期===\n"
    remindNearText = f"===临近特别日期===\n"
    if dateRemindResult:
        for obj in dateRemindResult:
            theDate :datetime.date = obj['date']
            theDict = {
                'date':obj['date'],
                'title':obj['title'],
            }
            if isEquelDate(today,theDate): # type: ignore
                dateList.append(theDict)
            elif theDate.day-today.day<=3:
                dateNearList.append(theDict)
    if len(dateList)>0:
        for obj in dateList: remindText+=f"{obj['title']}\n"
        for obj in dateNearList: remindNearText+=f"{obj['date']} {obj['title']}\n"
        for groupId in get_listening_groups():
            await bot.api.post_group_msg(group_id=groupId,text=remindText+remindNearText)
