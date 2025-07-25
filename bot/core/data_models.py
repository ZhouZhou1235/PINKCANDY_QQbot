# 数据模型

from dataclasses import dataclass
from typing import List, Optional

# 机器配置
@dataclass
class BotConfig:
    bot_name :str
    bot_info :str
    qq_number :str
    listen_qq_groups :List[int] # 监听的QQ群
    fixed_begin :str # 固定命令前缀
    function_commands :dict
    function_command_info :List[str] # 帮助文本
    MySQL_config :dict # MySQL数据库配置
    MemoryChatRobot_config :dict # 对话人工智能体配置
    GALLERY_SYSTEM_WEB :str # 幻想动物画廊后端地址
    GALLERY_WEB :str # 幻想动物画廊网站地址
    @classmethod
    def load(cls,obj:dict):
        return cls(
            bot_name=obj['bot_name'],
            bot_info=obj['bot_info'],
            qq_number=obj['qq_number'],
            listen_qq_groups=obj['listen_qq_groups'],
            fixed_begin=obj['fixed_begin'],
            function_commands=obj['function_commands'],
            function_command_info=obj['function_command_info'],
            MySQL_config=obj['MySQL_config'],
            MemoryChatRobot_config=obj['MemoryChatRobot_config'],
            GALLERY_SYSTEM_WEB=obj['GALLERY_SYSTEM_WEB'],
            GALLERY_WEB=obj['GALLERY_WEB'],
        )

# 群友
@dataclass
class GroupMember:
    group_id: int
    user_id: int
    nickname: str
    join_time: int
    level: Optional[str] # 群成员等级
    role: Optional[str] # member成员 admin管理 owner群主
    @classmethod
    def load(cls,obj:dict):
        return cls(
            group_id=obj['group_id'],
            user_id=obj['user_id'],
            nickname=obj['nickname'],
            join_time=obj['join_time'],
            level=obj.get('level'),
            role=obj.get('role','member'),
        )

# 幻想动物画廊 作品信息
@dataclass
class GalleryArtwork:
    id: str
    username: str
    filename: str
    title: str
    info: str
    time: str
    @classmethod
    def load(cls,obj:dict):
        return cls(
            id = obj['id'],
            username = obj['username'],
            filename = obj['filename'],
            title = obj['title'],
            info = obj['info'],
            time = obj['time'],
        )
