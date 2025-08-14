# 启动

from core.config_manager import config_manager
from core.bot_launcher import create_bot


if __name__=='__main__':
    bot = create_bot()
    bot.run(bt_uin=config_manager.bot_config.qq_number)
