# 由NapCatQQ/OneBot标准返回数据定义的数据模型
# 使用原生python数据模型类修饰器

from dataclasses import dataclass
from typing import Optional

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
            role=obj.get('role','member')
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
