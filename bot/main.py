# 启动

from core.global_area import g_bot_config
from core.bot_launcher import create_bot

if __name__=='__main__':
    bot = create_bot()
    bot.run(bt_uin=g_bot_config.qq_number)
