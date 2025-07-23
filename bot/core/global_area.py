# 全局空间

import json
import os
import random
from typing import Any, List
from core.connect_database import MySQLConnecter
from core.chat_robot import MemoryChatRobot
from core.data_models import BotConfig


# 得到指令对应的文本
def getCommendString(commendKey:str):
    return f"{g_bot_config.fixed_begin} {g_bot_config.function_commands[commendKey]}"

# 从列表中抽取指定数量元素
def randomGetListElements(l:List[Any],num:int):
    theList = l.copy()
    resultList = []
    if num<0 or num>len(theList): return None
    while len(resultList)<num:
        i = random.randint(0,len(theList))
        element = theList[i]
        theList.pop(i)
        resultList.append(element)
    return resultList

# 读取文件为字符串
def readFileAsString(path:str):
    string = ''
    with open(path,mode='r',encoding='UTF-8') as f:
        string = f.read()
    return string

# TODO 重写通用的事件冷却


g_workPath = os.getcwd()+'/bot' # vscode工作区
# g_workPath = os.getcwd()
g_configPath = g_workPath.replace("\\","/")+"/bot_config.json"
g_bot_config = BotConfig.load(json.loads(readFileAsString(g_configPath)))
g_memoryChatRobot = MemoryChatRobot(g_bot_config)
g_mySQLConnecter = MySQLConnecter(g_bot_config)
