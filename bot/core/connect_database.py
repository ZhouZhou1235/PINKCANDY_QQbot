# 连接数据库

import pymysql
from pymysql.cursors import DictCursor
from core.data_models import BotConfig


# MySQL数据库连接者
class MySQLConnecter:
    def __init__(self,config:BotConfig):
        self.connection = pymysql.connect(
            host=config.MySQL_config.get('host','localhost'),
            user=config.MySQL_config.get('user'),
            password=config.MySQL_config.get('password'), # type: ignore
            database=config.MySQL_config.get('database'),
            charset='utf8mb4',
            cursorclass=DictCursor,
            autocommit=True,
        ) # type: ignore
    # 查询数据
    def query_data(self,sql:str):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchone()
                if result:
                    next_result = cursor.fetchone()
                    if next_result:
                        return [result]+[next_result]+list(cursor.fetchall())
                    return [dict(result)]
                return None
        except Exception as e:
            print(f"PINKCANDY MYSQL ERROR:{e}")
            return None
    # 执行SQL语句
    def execute_query(self,sql:str,params=None):
        try:
            self.connection.ping(reconnect=True)
            with self.connection.cursor() as cursor:
                if params: return cursor.execute(sql,params)
                return cursor.execute(sql)
        except Exception as e:
            print(f"PINKCANDY MYSQL ERROR: {e}")
            return None
