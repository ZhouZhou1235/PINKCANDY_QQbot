# 对话人工智能体

import asyncio
import json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from typing import Dict, List
from pydantic import SecretStr
from core.data_models import BotConfig
from core.connect_database import MySQLConnecter


# 内存记忆人工智能体
class MemoryChatRobot:
    def __init__(self,config:BotConfig,db:MySQLConnecter):
        self.botConfig = config
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            base_url=config.DEEPSEEK_API,
            api_key=SecretStr(config.DEEPSEEK_API_KEY),
            temperature=0.25  # 温度
        )
        self.chat_histories: Dict[str,list] = {} # 对话记录存储
        self.db = db # 数据库连接者
    # 加载历史对话
    async def load_history(self,session_id:str):
        sql = f"""
            SELECT history_json
            FROM chat_memories
            WHERE session_id='{session_id}'
        """
        result = self.db.query_data(sql)
        print(f"load_history {result}")
        return json.loads(result['history_json']) if result else [] # type: ignore
    # 对话保存到数据库
    async def save_history(self,session_id:str,history:List[dict]):
        try:
            # 参数化查询
            history_json = json.dumps(history,ensure_ascii=False)
            sql = """
                INSERT INTO chat_memories (session_id,history_json) 
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE history_json=%s
            """
            self.db.execute_query(sql,(session_id,history_json,history_json))
        except Exception as e:
            print(f"PINKCANDY MYSQL SAVE ERROR: {e}")
    # 获取对话链
    def get_chain(self,session_id:str):
        prompt = ChatPromptTemplate.from_messages([
            ("system",self.botConfig.aichat_system_prompt),
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
            history = await self.load_history(session_id)
            user_msg = {"type": "human","content": user_input}
            history.append(user_msg)
            self.save_message(session_id,user_msg)
            if session_id not in self.chat_histories:
                self.chat_histories[session_id] = history.copy()
            else:
                self.chat_histories[session_id] = history.copy()
            chain = self.get_chain(session_id)
            response = await asyncio.to_thread(
                chain.invoke,
                {
                    "input": user_input,
                    "session_id": session_id,
                    "history": self.format_history(session_id)
                }
            )
            ai_msg = {"type": "ai", "content": response.content}
            history.append(ai_msg)
            self.save_message(session_id, ai_msg)
            await self.save_history(session_id, history)
            return response.content
        except Exception as e:
            print(f"PINKCANDY CHAT ERROR: {e}")
