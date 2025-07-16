from core.bot_config import Config
from ncatbot.core import BotClient
from ncatbot.utils import get_log

# 粉糖终端
class QQbot:
    def __init__(self):
        self.bot_config = Config() # 配置
        self.bot_log = get_log() # 聊天记录器
        self.bot_client = BotClient() # ncatbot客户端
    def bot_run(self):
        self.bot_client.run(bt_uin=self.bot_config.qq_number)
