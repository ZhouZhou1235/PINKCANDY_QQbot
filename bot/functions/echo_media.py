# 机器回复媒体

import json
import random
import requests
from ncatbot.core import GroupMessage
from core.napcat_api import *
from core.data_models import *
from core.global_utils import *
from core.config_manager import config_manager


# 在群聊中回复媒体
@eventCoolDown(5)
async def group_echo_media(bot:BotClient,message:GroupMessage):
    if message.group_id in config_manager.bot_config.listen_qq_groups:
        command = getCommendString("get_gallery_artwork")
        if message.raw_message[:len(command)] == command:
            gallery_system_web = "https://gallery-system.pinkcandy.top"
            gallery_web = "https://gallery.pinkcandy.top"
            try:
                searchtext = message.raw_message[len(command):]
                res = requests.get(gallery_system_web+f"/core/searchPinkCandy?searchtext={searchtext}")
                searchPinkCandyDict = json.loads(res.text)
                artworkList :list = searchPinkCandyDict['artwork']
                if searchPinkCandyDict and len(artworkList)>0:
                    theArtwork :GalleryArtwork = GalleryArtwork.load(random.choice(artworkList))
                    imageurl = gallery_system_web+f"/files/gallery/{theArtwork.filename}"
                    echoText = f"[CQ:image,summary=[{theArtwork.title}],url={imageurl}]\n"
                    echoText += f"《{theArtwork.title}》\n{theArtwork.info}\n"
                    echoText += f"{gallery_web}/artwork/{theArtwork.id}\n"
                    bot.api.post_group_msg_sync(group_id=message.group_id,text=echoText)
                else: await message.reply(text="PINKCANDY: no artwork found")
            except Exception as e: print(e)
