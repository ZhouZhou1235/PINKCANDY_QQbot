# 全局通用工具函数

import random
from typing import Any, List
from core.config_manager import config_manager


# 得到指令对应的文本
def getCommendString(commendKey:str):
    return f"{config_manager.bot_config.fixed_begin} {config_manager.bot_config.function_commands[commendKey]}"

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

# TODO 重写事件冷却
