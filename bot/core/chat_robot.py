# 对话人工智能体

import asyncio
import json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from typing import Dict, List
from pydantic import SecretStr
from core.data_models import BotConfig
from core.global_area import g_mySQLConnecter
# TODO 解决循环导入报错


# 内存记忆人工智能体
class MemoryChatRobot:
    def __init__(self,config:BotConfig):
        self.botConfig = config
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            base_url=config.DEEPSEEK_API,
            api_key=SecretStr(config.DEEPSEEK_API_KEY),
            temperature=0.25  # 温度
        )
        self.chat_histories: Dict[str,list] = {} # 对话记录存储
        self.db = g_mySQLConnecter # 数据库
    # 加载历史对话
    async def load_history(self,session_id:str):
        sql = f"""
            SELECT history_json
            FROM chat_memories
            WHERE session_id='{session_id}'
        """
        result = self.db.query_data(sql)
        print(f"load_history {result}")
        return json.loads(result['history_json']) if result else []
    # 对话保存到数据库
    async def save_history(self,session_id:str,history:List[dict]):
        history_json = json.dumps(history,ensure_ascii=False)
        sql = f"""
            INSERT INTO chat_memories (session_id,history_json) 
            VALUES ('{session_id}','{history_json}')
            ON DUPLICATE KEY UPDATE history_json='{history_json}'
        """
        self.db.execute_query(sql)
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
            history.append({"type":"human","content":user_input})
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
            history.append({"type":"ai","content":response.content})
            await self.save_history(session_id,history)
            return response.content
        except Exception as e: print(f"PINKCANDY ERROR:{e}")
