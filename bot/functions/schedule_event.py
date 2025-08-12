# 定时执行事件

import datetime
from ncatbot.core import BotClient
from core.config_manager import config_manager



# 每日执行一次
async def schedule_oneday(bot:BotClient):
    # TODO 日期提醒
    dateRemindResult :list = config_manager.mysql_connector.query_data("SELECT * FROM date_reminder")
    today = datetime.date.today()
    if dateRemindResult:
        for obj in dateRemindResult:
            if today==obj['date']:
                print(obj['title'])
