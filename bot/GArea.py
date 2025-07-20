# 全局空间

import random
from typing import Any, List
from core.bot_config import Config

# === 固定量 ===
GALLERY_SYSTEM_WEB = "https://gallery-system.pinkcandy.top"
GALLERY_WEB = "https://gallery.pinkcandy.top"


# === 变量 ===
g_bot_config = Config()
# g_can_use_num = 10


# === 函数 ===

# 使用数恢复
# def recoverUseNum():
#     global g_can_use_num
#     if g_can_use_num<10:
#         g_can_use_num += 1

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
