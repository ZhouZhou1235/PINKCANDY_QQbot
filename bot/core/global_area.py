# 全局空间

import json
import os
import random
import time
from typing import Any, List
from functools import wraps
from ncatbot.core import GroupMessage,PrivateMessage
import asyncio
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from typing import Dict
from pydantic import SecretStr
from core.data_models import BotConfig


# === 函数 ===

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


# === 类 ===

# 事件冷却
class EventCoolDown:
    # 用法
    # 实例化 用作函数的修饰器
    # eventCoolDown = EventCoolDown(5)
    # @eventCoolDown
    # def func(message): pass
    def __init__(self,interval):
        self.interval = interval # 冷却时间
        self.last_trigger = {}
    def __call__(self,func:Any):
        @wraps(func)
        async def wrapper(message:GroupMessage|PrivateMessage,*args,**kwargs):
            command = getCommendString(func.__name__)
            # 放行非目标命令
            if not message.raw_message.startswith(command):
                return await func(message,*args,**kwargs)
            key = f"{message.group_id}_{func.__name__}"
            now = time.time()
            if key in self.last_trigger and now - self.last_trigger[key] < self.interval:
                await message.reply("PINKCANDY: too fast! wait a few seconds.")
                return
            self.last_trigger[key] = now
            return await func(message, *args, **kwargs)
        return wrapper

# 对话人工智能体
# TODO 持久化储存记忆
class MemoryChatRobot:
    def __init__(self,url:str,apikey:str):
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            base_url=url,
            api_key=SecretStr(apikey),
            temperature=0.25  # 温度
        )
        self.chat_histories: Dict[str,list] = {} # 对话记录存储
    # 获取对话链
    def get_chain(self,session_id:str):
        prompt = ChatPromptTemplate.from_messages([
            ("system",g_bot_config.aichat_system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ])
        chain = (
            RunnablePassthrough.assign(
                history=lambda x: self.format_history(x["session_id"])
            )
            | prompt
            | self.llm
        )
        return chain
    # 格式化消息
    def format_history(self,session_id:str):
        from langchain_core.messages import AIMessage, HumanMessage
        formatted = []
        for msg in self.chat_histories.get(session_id, []):
            if msg["type"] == "human":
                formatted.append(HumanMessage(content=msg["content"]))
            else:
                formatted.append(AIMessage(content=msg["content"]))
        return formatted
    # 保存消息
    def save_message(self, session_id:str,message: dict):
        if session_id not in self.chat_histories:
            self.chat_histories[session_id] = []
        self.chat_histories[session_id].append(message)
    # 对话
    async def chat(self,session_id:str,user_input:str):
        try:
            self.save_message(session_id,{
                "type": "human",
                "content": user_input
            })
            chain = self.get_chain(session_id)
            response = await asyncio.to_thread(
                chain.invoke,
                {"input":user_input,"session_id":session_id}
            )
            self.save_message(session_id, {
                "type": "ai",
                "content": response.content
            })
            return response.content
        except Exception as e: print(f"PINKCANDY ERROR:{e}")


# === 固定量 ===
GALLERY_SYSTEM_WEB = "https://gallery-system.pinkcandy.top"
GALLERY_WEB = "https://gallery.pinkcandy.top"
DEEPSEEK_API = "https://api.deepseek.com"
DEEPSEEK_API_KEY = "sk-69d85f5be9184810970ccf2d4add0474"


# === 变量 ===
g_workPath = os.getcwd()+'/bot' # vscode工作区
# g_workPath = os.getcwd()
g_bot_config = BotConfig.load(json.loads(readFileAsString(g_workPath.replace("\\","/")+"/bot_config.json")))
g_memoryChatRobot = MemoryChatRobot(DEEPSEEK_API,DEEPSEEK_API_KEY)
g_eventCoolDown = EventCoolDown(5)
