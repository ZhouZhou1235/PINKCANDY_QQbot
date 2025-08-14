# 定时执行事件

import datetime
from ncatbot.core import BotClient
from functions.share_functions import get_dates
from core.global_utils import get_listening_groups, isEquelDate

# 每日执行一次
async def schedule_oneday(bot:BotClient):
    # 日期提醒
    dateRemindResult :list = get_dates() # type: ignore
    today = datetime.date.today()
    dateList = []
    remindText = f"==={today.month}月{today.day}日 特别日期===\n"
    if dateRemindResult:
        for obj in dateRemindResult:
            theDate = obj['date']
            if isEquelDate(today,theDate): # type: ignore
                dateList.append({
                    'date':obj['date'],
                    'title':obj['title'],
                })
    if len(dateList)>0:
        for obj in dateList:
            remindText += f"{obj['title']}\n"
        for groupId in get_listening_groups():
            await bot.api.post_group_msg(group_id=groupId,text=remindText)
