# 启动

from core.config_manager import config_manager
from core.bot_launcher import create_bot,add_event_to_bot,add_schedule_to_bot


if __name__=='__main__':
    bot = create_bot()
    add_event_to_bot(bot)
    add_schedule_to_bot(bot)
    bot.run(bt_uin=config_manager.bot_config.qq_number)
