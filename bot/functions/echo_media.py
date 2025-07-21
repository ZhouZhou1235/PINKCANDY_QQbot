# 机器回复媒体

import json
import random
import requests
from ncatbot.core import GroupMessage
from core.napcat_api import *
from core.data_models import *
from GArea import *


# === 群聊 ===

# 来点粉糖
@g_eventCoolDown
async def get_gallery_artwork(message:GroupMessage):
    if message.group_id in g_bot_config.listen_qq_groups:
        command = getCommendString("get_gallery_artwork")
        if message.raw_message[:len(command)] == command:
            try:
                searchtext = message.raw_message[len(command):]
                res = requests.get(GALLERY_SYSTEM_WEB+f"/core/searchPinkCandy?searchtext={searchtext}")
                searchPinkCandyDict = json.loads(res.text)
                artworkList :list = searchPinkCandyDict['artwork']
                if searchPinkCandyDict and len(artworkList)>0:
                    theArtwork :GalleryArtwork = GalleryArtwork.load(random.choice(artworkList))
                    imageurl = GALLERY_SYSTEM_WEB+f"/files/gallery/{theArtwork.filename}"
                    echoText = f"[CQ:image,summary=[{theArtwork.title}],url={imageurl}]\n"
                    echoText += f"《{theArtwork.title}》\n{theArtwork.info}\n"
                    echoText += f"{GALLERY_WEB}/artwork/{theArtwork.id}\n"
                    await message.reply(text=echoText)
                else: await message.reply(text="PINKCANDY: no artwork found")
            except Exception as e: print(e)
