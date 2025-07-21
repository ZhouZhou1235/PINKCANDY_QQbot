# 大模型对话

import asyncio
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from typing import Dict
from pydantic import SecretStr
from core.bot_config import Config

# TODO 持久化储存记忆

# 对话人工智能体
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
            ("system",Config().aichat_system_prompt),
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
