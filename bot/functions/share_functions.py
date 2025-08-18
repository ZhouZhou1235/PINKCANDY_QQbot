# 共用的函数

from core.config_manager import config_manager


# 查询特别日期
def get_dates(): return config_manager.mysql_connector.query_data("SELECT * FROM date_reminder")
