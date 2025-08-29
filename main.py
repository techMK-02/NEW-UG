# 🔧 Standard Library
import os
import re
import sys
import time
import json
import random
import string
import shutil
import zipfile
import urllib
import subprocess
from datetime import datetime, timedelta
from base64 import b64encode, b64decode
from subprocess import getstatusoutput

# 🕒 Timezone
import pytz

# 📦 Third-party Libraries
import aiohttp
import aiofiles
import requests
import asyncio
import ffmpeg
import m3u8
import cloudscraper
import yt_dlp
import tgcrypto
from bs4 import BeautifulSoup
from pytube import YouTube
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ⚙️ Pyrogram
from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from pyrogram.errors import (
    FloodWait,
    BadRequest,
    Unauthorized,
    SessionExpired,
    AuthKeyDuplicated,
    AuthKeyUnregistered,
    ChatAdminRequired,
    PeerIdInvalid,
    RPCError
)
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified

# 🧠 Bot Modules
import auth
import ug as helper

from clean import register_clean_handler
from logs import logging
from utils import progress_bar
from vars import *
from db import db
from pyromod import listen
import apixug
from apixug import SecureAPIClient

client = SecureAPIClient()
apis = client.get_apis()

auto_flags = {}
auto_clicked = False

# Global variables
watermark = "GovtXExam"  # Default value
count = 0
userbot = None
timeout_duration = 300  # 5 minutes


# Initialize bot with random session
bot = Client(
    "UG",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=300,
    sleep_threshold=60,
)

processing_request = False
cancel_requested = False
cancel_message = None

# Register command handlers
register_clean_handler(bot)

# Re-register auth commands
bot.add_handler(MessageHandler(auth.add_user_cmd, filters.command("add") & filters.private))
bot.add_handler(MessageHandler(auth.remove_user_cmd, filters.command("remove") & filters.private))
bot.add_handler(MessageHandler(auth.list_users_cmd, filters.command("users") & filters.private))
bot.add_handler(MessageHandler(auth.my_plan_cmd, filters.command("plan") & filters.private))

cookies_file_path = os.getenv("cookies_file_path", "youtube_cookies.txt")
api_url = "http://master-api-v3.vercel.app/"
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzkxOTMzNDE5NSIsInRnX3VzZXJuYW1lIjoi4p61IFtvZmZsaW5lXSIsImlhdCI6MTczODY5MjA3N30.SXzZ1MZcvMp5sGESj0hBKSghhxJ3k1GTWoBUbivUe1I"
photologo = 'https://img.freepik.com/premium-vector/ug-logo_1172241-4712.jpg?semt=ais_hybrid&w=740&q=80' #https://envs.sh/GV0.jpg
photoyt = 'https://tinypic.host/images/2025/03/18/YouTube-Logo.wine.png' #https://envs.sh/GVi.jpg
photocp = 'https://tinypic.host/images/2025/03/28/IMG_20250328_133126.jpg'
photozip = 'https://envs.sh/cD_.jpg'
UNSPLASH_URL = "https://unsplash.com/napi/search/illustrations/related?query=nature"



# Inline keyboard for start command
BUTTONSCONTACT = InlineKeyboardMarkup([[InlineKeyboardButton(text="📞 Contact", url="https://t.me/MrFrontMan001")]])
keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="🛠️ Help", url="https://t.me/MrFrintMan001")        ],
    ]
)


def escape_md(text: str) -> str:
    # MarkdownV2 escaping
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return "".join("\\" + c if c in escape_chars else c for c in text)

async def get_random_unsplash_image():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(UNSPLASH_URL) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and isinstance(data, list):
                        img = random.choice(data)
                        return img["urls"]["regular"]
    except Exception as e:
        print(f"[IMG] Error fetching Unsplash image: {e}")
    return photologo


        
@bot.on_message(filters.command("cookies") & filters.private)
async def cookies_handler(client: Client, m: Message):
    await m.reply_text(
        "Please upload the cookies file (.txt format).",
        quote=True
    )

    try:
        # Wait for the user to send the cookies file
        input_message: Message = await client.listen(m.chat.id)

        # Validate the uploaded file
        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await m.reply_text("Invalid file type. Please upload a .txt file.")
            return

        # Download the cookies file
        downloaded_path = await input_message.download()

        # Read the content of the uploaded file
        with open(downloaded_path, "r") as uploaded_file:
            cookies_content = uploaded_file.read()

        # Replace the content of the target cookies file
        with open(cookies_file_path, "w") as target_file:
            target_file.write(cookies_content)

        await input_message.reply_text(
            "✅ Cookies updated successfully.\n📂 Saved in `youtube_cookies.txt`."
        )

    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")

@bot.on_message(filters.command(["t2t"]))
async def text_to_txt(client, message: Message):
    user_id = str(message.from_user.id)
    # Inform the user to send the text data and its desired file name
    editable = await message.reply_text(f"<blockquote>Welcome to the Text to .txt Converter!\nSend the **text** for convert into a `.txt` file.</blockquote>")
    input_message: Message = await bot.listen(message.chat.id)
    if not input_message.text:
        await message.reply_text("**Send valid text data**")
        return

    text_data = input_message.text.strip()
    await input_message.delete()  # Corrected here
    
    await editable.edit("**🔄 Send file name or send /d for filename**")
    inputn: Message = await bot.listen(message.chat.id)
    raw_textn = inputn.text
    await inputn.delete()  # Corrected here
    await editable.delete()

    if raw_textn == '/d':
        custom_file_name = 'txt_file'
    else:
        custom_file_name = raw_textn

    txt_file = os.path.join("downloads", f'{custom_file_name}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)  # Ensure the directory exists
    with open(txt_file, 'w') as f:
        f.write(text_data)
        
    await message.reply_document(document=txt_file, caption=f"`{custom_file_name}.txt`\n\n<blockquote>You can now download your content! 📥</blockquote>")
    os.remove(txt_file)

# Define paths for uploaded file and processed file
UPLOAD_FOLDER = '/path/to/upload/folder'
EDITED_FILE_PATH = '/path/to/save/edited_output.txt'

@bot.on_message(filters.command("getcookies") & filters.private)
async def getcookies_handler(client: Client, m: Message):
    try:
        # Send the cookies file to the user
        await client.send_document(
            chat_id=m.chat.id,
            document=cookies_file_path,
            caption="Here is the `youtube_cookies.txt` file."
        )
    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")

@bot.on_message(filters.command(["reset"]) )
async def restart_handler(_, m):
    if m.chat.id != OWNER_ID:
        return
    else:
        await m.reply_text("𝐁𝐨𝐭 𝐢𝐬 𝐑𝐞𝐬𝐞𝐭𝐢𝐧𝐠...", True)
        os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command("stop") & filters.private)
async def cancel_handler(client: Client, m: Message):
    global processing_request, cancel_requested, cancel_message  
    if not db.is_user_authorized(m.from_user.id, bot.me.username):
        await m.reply_text("❌ You are not authorized to use this command.")
        return
    else:
        if processing_request:
            cancel_requested = True
            await m.delete()
            cancel_message = await m.reply_text("**🚦 Process cancel request received. Stopping after current process...**")
        else:
            cancel_message = None
            await m.reply_text("**⚡ No active process to cancel.**")
        

@bot.on_message(filters.command("start") & filters.private)
async def start(bot: Client, m: Message):
    user_id = m.from_user.id
    first_name = m.from_user.first_name

    is_authorized = db.is_user_authorized(user_id, bot.me.username)
    is_admin = db.is_admin(user_id)

    img_url = await get_random_unsplash_image()

    if not is_authorized:
        await m.reply_photo(
            photo= 'https://files.catbox.moe/1w7a78.jpg',
            caption=(
                "𓆩🔒𓆪 **ᴀᴄᴄᴇꜱꜱ ʀᴇǫᴜɪʀᴇᴅ**\n\n"
                "𓆩💰𓆪 **ᴘʀɪᴄɪɴɢ**\n"
                "• 1 ᴡᴇᴇᴋ — ₹150\n"
                "• 1 ᴍᴏɴᴛʜ — ₹400"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 sᴇɴᴅ ɪᴅ", callback_data="send_id_admin")],
                [InlineKeyboardButton("✨ ᴄᴏɴᴛᴀᴄᴛ", url="https://t.me/mrfrontman001")]
            ])
        )
        return

    commands_list = (
        "𓆩🤖𓆪 **ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ**\n"
        "• /drm — ꜱᴛᴀʀᴛ ᴜᴘʟᴏᴀᴅɪɴɢ\n"
        "➜ 🔓 • ᴀᴜᴛᴏ ᴅʀᴍ ᴅᴇᴄʀʏᴘᴛɪᴏɴ"
        "• /plan — ᴠɪᴇᴡ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ\n"
    )
    if is_admin:
        commands_list += (
            "\n𓆩👑𓆪 **ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅꜱ**\n"
            "• `/users` — ʟɪꜱᴛ ᴀʟʟ ᴜꜱᴇʀꜱ\n"
        )

    features_list = (
        "𓆩💎𓆪 **ꜰᴇᴀᴛᴜʀᴇꜱ ʏᴏᴜ'ʟʟ ʟᴏᴠᴇ:**\n"
        "➜ 🔓 • ᴀᴜᴛᴏ ᴅʀᴍ ᴅᴇᴄʀʏᴘᴛɪᴏɴ\n"
        "➜ ⚡ • ᴘʀᴇᴍɪᴜᴍ Qᴜᴀʟɪᴛʏ\n"
        "➜ 📚 • ʙᴀᴛᴄʜ ꜱᴜᴘᴘᴏʀᴛ\n"
        "➜ 🚀 • ᴜʟᴛʀᴀ-ꜰᴀꜱᴛ ꜱᴘᴇᴇᴅ\n"
    )

    await m.reply_photo(
        photo=img_url,
        caption=(
            f"╭━━━━━━━━━━━━━━━━━━━━╮\n┃  ✨ ʜᴇʏ {first_name} ❤️\n┃  🦎 ɪ'ᴍ ʏᴏᴜʀ ᴅʀᴍ ᴡɪᴢᴀʀᴅ!\n╰━━━━━━━━━━━━━━━━━━━━╯**\n\n"
            f"{features_list}\n"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✨ ᴄᴏɴᴛᴀᴄᴛ", url="https://t.me/ItsUGxBot")]
        ])
    )

def auth_check_filter(_, client, message):
    try:
        return db.is_user_authorized(message.from_user.id, client.me.username)
    except Exception:
        return False

auth_filter = filters.create(auth_check_filter)

@bot.on_message(~auth_filter & filters.private & filters.command)
async def unauthorized_handler(client, message: Message):
    await message.reply(
        "<b>🔒 access restricted</b>\n\n"
        "**You need to have an active subscription to use this bot**.\n"
        "__Please contact admin to get premium access.__",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("send id to admin", callback_data="send_id_admin")
        ]])
    )

@bot.on_callback_query(filters.regex("^send_id_admin$"))
async def send_id_to_admin(bot: Client, cq: CallbackQuery):
    user = cq.from_user
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        await bot.send_message(
            OWNER_ID,
            f"📩 <b>Access Request</b>\n\n"
            f"**👤 Name:** {user.first_name or ''} {user.last_name or ''}\n"
            f"**🔗 Username:** @{user.username if user.username else 'N/A'}\n"
            f"**🆔 User ID:** <code>{user.id}</code>\n"
            f"**⏰ Time:** {time_now}\n"
            f"**🔗 LNK:** [{user.first_name or 'N/A'}](tg://openmessage?user_id={user.id})"
        )
        await cq.answer("🆔 Your ID has been sent to Frontman !!", show_alert=True)

    except Exception as e:
        # Agar admin ko send fail ho jaye to user ko bata do
        await cq.answer("❌ Unable to send to admin, Use /id and copy id and send to admin.", show_alert=True)

@bot.on_message(filters.command(["id"]))
async def id_command(client, message: Message):
    chat_id = message.chat.id
    await message.reply_text(
        f"<blockquote>**The ID of this chat id is**:</blockquote>\n`{chat_id}`"
    )

def to_small_caps(text):
    mapping = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ',
        'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
        'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ',
        'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',

        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ꜰ', 'G': 'ɢ',
        'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ',
        'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 's', 'T': 'ᴛ', 'U': 'ᴜ',
        'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ',
    }
    return ''.join(mapping.get(c, c) for c in text)

@bot.on_message(filters.command(["drm"]) & auth_filter)
async def txt_handler(bot: Client, m: Message):  
    global processing_request, cancel_requested, cancel_message
    # Get bot username
    bot_info = await bot.get_me()
    bot_username = bot_info.username

    # Check authorization
    if m.chat.type == "channel":
        if not db.is_channel_authorized(m.chat.id, bot_username):
            return
    else:
        if not db.is_user_authorized(m.from_user.id, bot_username):
            await m.reply_text("❌ You are not authorized to use this command.")
            return
    
    editable = await m.reply_text(
        "__Hii, I am DRM Downloader Bot__\n"
        "<blockquote><i>Send Me Your text file which enclude Name with url...\nE.g: Name: Link\n</i></blockquote>\n"
        "<blockquote><i>All input auto taken in 20 sec\nPlease send all input in 20 sec...\n</i></blockquote>"
    )

    input: Message = await bot.listen(editable.chat.id)
    
    # Check if a document was actually sent
    if not input.document:
        await m.reply_text("<b>❌ Please send a text file!</b>")
        return
        
    # Check if it's a text file
    if not input.document.file_name.endswith('.txt'):
        await m.reply_text("<b>❌ Please send a .txt file!</b>")
        return
        
    x = await input.download()
    await input.delete(True)
    file_name, ext = os.path.splitext(os.path.basename(x))  # Extract filename & extension
    path = f"./downloads/{m.chat.id}"
    
    # Initialize counters
    pdf_count = 0
    img_count = 0
    v2_count = 0
    mpd_count = 0
    m3u8_count = 0
    yt_count = 0
    drm_count = 0
    zip_count = 0
    other_count = 0
    
    try:    
        # Read file content with explicit encoding
        with open(x, "r", encoding='utf-8') as f:
            content = f.read()
            
        # Debug: Print file content
        print(f"File content: {content[:500]}...")  # Print first 500 chars
            
        content = content.split("\n")
        content = [line.strip() for line in content if line.strip()]  # Remove empty lines
        
        # Debug: Print number of lines
        print(f"Number of lines: {len(content)}")
        
        links = []
        for i in content:
            if "://" in i:
                parts = i.split("://", 1)
                if len(parts) == 2:
                    name = parts[0]
                    url = parts[1]
                    links.append([name, url])
                    
                if ".pdf" in url:
                    pdf_count += 1
                elif url.endswith((".png", ".jpeg", ".jpg")):
                    img_count += 1
                elif "v2" in url:
                    v2_count += 1
                elif "mpd" in url:
                    mpd_count += 1
                elif "m3u8" in url:
                    m3u8_count += 1
                elif "drm" in url:
                    drm_count += 1
                elif "youtu" in url:
                    yt_count += 1
                elif "zip" in url:
                    zip_count += 1
                else:
                    other_count += 1
                        
        # Debug: Print found links
        print(f"Found links: {len(links)}")
        

        
    except UnicodeDecodeError:
        await m.reply_text("<b>❌ File encoding error! Please make sure the file is saved with UTF-8 encoding.</b>")
        os.remove(x)
        return
    except Exception as e:
        await m.reply_text(f"<b>🔹Error reading file: {str(e)}</b>")
        os.remove(x)
        return
    
    await editable.edit(
    f"**Total 🔗 {len(links)} links found in TXT File\n\n"
    f"PDF : {pdf_count}   Img : {img_count}   V2 : {v2_count} \n"
    f"drm : {drm_count}   mpd : {mpd_count}   m3u8 : {m3u8_count}\n"
    f"YT : {yt_count}   ZIP : {zip_count}\n"
    f"Others : {other_count}\n\n"
    f"Send from where you want to download. Initial is `1`**",
  
)
    
    chat_id = editable.chat.id
    timeout_duration = 3 if auto_flags.get(chat_id) else 20
    try:
        input0: Message = await bot.listen(editable.chat.id, timeout=timeout_duration)
        raw_text = input0.text
        await input0.delete(True)
    except asyncio.TimeoutError:
        raw_text = '1'
    
    if int(raw_text) > len(links) :
        await editable.edit(f"**🔹Enter number in range of Index (01-{len(links)})**")
        processing_request = False  # Reset the processing flag
        await m.reply_text("**🔹Exiting Task......  **")
        return
    
    chat_id = editable.chat.id
    timeout_duration = 3 if auto_flags.get(chat_id) else 20
    await editable.edit(f"**Enter Batch Name or send /d**")
    try:
        input1: Message = await bot.listen(editable.chat.id, timeout=timeout_duration)
        raw_text0 = input1.text
        await input1.delete(True)
    except asyncio.TimeoutError:
        raw_text0 = '/d'
    
    if raw_text0 == '/d':
        b_name = file_name.replace('_', ' ')
    else:
        b_name = raw_text0
    
    chat_id = editable.chat.id
    timeout_duration = 3 if auto_flags.get(chat_id) else 20
    await editable.edit("**1. Send Video Resolution \n 2. Send Video Quality\n⏩ `360` | `480` | `720` | `1080`**")
    try:
        input2: Message = await bot.listen(editable.chat.id, timeout=timeout_duration)
        raw_text2 = input2.text
        await input2.delete(True)
    except asyncio.TimeoutError:
        raw_text2 = '480'
    quality = f"{raw_text2}p"
    try:
        if raw_text2 == "144":
            res = "256x144"
        elif raw_text2 == "240":
            res = "426x240"
        elif raw_text2 == "360":
            res = "640x360"
        elif raw_text2 == "480":
            res = "854x480"
        elif raw_text2 == "720":
            res = "1280x720"
        elif raw_text2 == "1080":
            res = "1920x1080" 
        else: 
            res = "UN"
    except Exception:
            res = "UN"
    chat_id = editable.chat.id
    timeout_duration = 3 if auto_flags.get(chat_id) else 20

    await editable.edit("**1. 🆎 Enter watermark text \n2. 🖼️ Send /d for default watermark**")
    try:
        inputx: Message = await bot.listen(editable.chat.id, timeout=timeout_duration)
        raw_textx = inputx.text
        await inputx.delete(True)
    except asyncio.TimeoutError:
        raw_textx = '/d'
    
    # Define watermark variable based on input
    global watermark
    if raw_textx == '/d':
        watermark = "GovtXExam"
    else:
        watermark = raw_textx
    
    await editable.edit(f"__**1. Enter Credit Name For Caption\n2. Send /d Default Credit**")
    try:
        input3: Message = await bot.listen(editable.chat.id, timeout=timeout_duration)
        raw_text3 = input3.text
        await input3.delete(True)
    except asyncio.TimeoutError:
        raw_text3 = '/d' 
        
    if raw_text3 == '/d':
        CR = f"{CREDIT}"
    elif "," in raw_text3:
        CR, PRENAME = raw_text3.split(",")
    else:
        CR = raw_text3
    chat_id = editable.chat.id
    timeout_duration = 3 if auto_flags.get(chat_id) else 20
    await editable.edit(f"**1. Send Token For Encrypt TXTS like PW \n2. Send /d if uploading normal TXTS**")
    try:
        input4: Message = await bot.listen(editable.chat.id, timeout=timeout_duration)
        raw_text4 = input4.text
        await input4.delete(True)
    except asyncio.TimeoutError:
        raw_text4 = '/d'


    chat_id = editable.chat.id
    timeout_duration = 3 if auto_flags.get(chat_id) else 20

    if auto_flags.get(chat_id):
        await editable.edit("**Using AUTO Topic Uploader**\n\n<blockquote><b>Topic will be fetched by Automatically...</b></blockquote>")
        raw_text5 = "yes"
    else:
        await editable.edit("**1. Send `yes` For Topic Wise Uploading \n2. Send /d For default uploading** \n\n")
        try:
            input5: Message = await bot.listen(chat_id, timeout=timeout_duration)
            raw_text5 = input5.text
            await input5.delete(True)
        except asyncio.TimeoutError:
            raw_text5 = "/d"

    await editable.edit("**1. Send Photo or Photo URL for Thumbnail\n 2. Send /d for default Thumbnail**\n")
    thumb = "/d"  # Set default value
    try:
        input6 = await bot.listen(chat_id=m.chat.id, timeout=timeout_duration)
        
        if input6.photo:
            # If user sent a photo
            if not os.path.exists("downloads"):
                os.makedirs("downloads")
            temp_file = f"downloads/thumb_{m.from_user.id}.jpg"
            try:
                # Download photo using correct Pyrogram method
                await bot.download_media(message=input6.photo, file_name=temp_file)
                thumb = temp_file
                await editable.edit("**✅ Custom thumbnail saved successfully!**")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Error downloading thumbnail: {str(e)}")
                await editable.edit("**⚠️ Failed to save thumbnail! Using default.**")
                thumb = "/d"
                await asyncio.sleep(1)
        elif input6.text:
            if input6.text == "/d":
                thumb = "/d"
                await editable.edit("**🖼️ Using default thumbnail.**")
                await asyncio.sleep(1)
            elif input6.text == "/skip":
                thumb = "no"
                await editable.edit("**⏭️ Skipping thumbnail.**")
                await asyncio.sleep(1)
            else:
                await editable.edit("**⚠️ Invalid input! Using default thumbnail.**")
                await asyncio.sleep(1)
        await input6.delete(True)
    except asyncio.TimeoutError:
        await editable.edit("**⚠️ Timeout! Using default thumbnail.**")
        await asyncio.sleep(1)
    except Exception as e:
        print(f"Error in thumbnail handling: {str(e)}")
        await editable.edit("**⚠️ Error! Using default thumbnail.**")
        await asyncio.sleep(1)
 
    await editable.edit("__**1. Send /d For Uploading Files In Chat\n2. Send Channel Id For Uploading in Channel 3. Send Group Id For Topic Wise Upload** \n\n<blockquote>Make Me Admin in your channel or group\nsend /id in channel\nyou get a numerical id send that me</blockquote>")
    try:
        input7: Message = await bot.listen(editable.chat.id, timeout=timeout_duration)
        raw_text7 = input7.text
        await input7.delete(True)
    except asyncio.TimeoutError:
        raw_text7 = '/d'

    if "/d" in raw_text7:
        channel_id = m.chat.id
    else:
        channel_id = raw_text7    
    await editable.delete()

    # Prepare topic index tracking when topic-wise is ON
    topic_first_message_links = {}
    chat_obj = await bot.get_chat(channel_id)
    if raw_text5 == "yes":
        try:
            stored_topics = db.get_topic_index(m.from_user.id, bot_username, channel_id, b_name)
            if isinstance(stored_topics, dict) and stored_topics:
                topic_first_message_links.update(stored_topics)
        except Exception:
            pass
    def _build_msg_link(chat, message_id):
        try:
            username = getattr(chat, "username", None)
            if username:
                return f"https://t.me/{username}/{message_id}"
            chat_id_val = getattr(chat, "id", channel_id)
            chat_id_val = int(chat_id_val)
            if chat_id_val < 0:
                cid = str(chat_id_val)
                if cid.startswith("-100"):
                    cid = cid[4:]
                else:
                    cid = str(abs(chat_id_val))
                return f"https://t.me/c/{cid}/{message_id}"
        except Exception:
            pass
        return None

    try:
        if raw_text == "1":
            batch_message = await bot.send_message(chat_id=channel_id, text=f"<blockquote><b>🎯Target Batch : {b_name}</b></blockquote>")
            if "/d" not in raw_text7:
                await bot.send_message(chat_id=m.chat.id, text=f"<blockquote><b><i>🎯Target Batch : {b_name}</i></b></blockquote>\n\n🔄 Your Task is under processing, please check your Set Channel📱. Once your task is complete, I will inform you 📩")
                await bot.pin_chat_message(channel_id, batch_message.id)
                message_id = batch_message.id + 1
                await bot.delete_messages(channel_id, message_id)
                await bot.pin_chat_message(channel_id, batch_message.id)

        else:
             if "/d" not in raw_text7:
                await bot.send_message(chat_id=m.chat.id, text=f"<blockquote><b><i>🎯Target Batch : {b_name}</i></b></blockquote>\n\n🔄 Your Task is under processing, please check your Set Channel📱. Once your task is complete, I will inform you 📩")
    except Exception as e:
        await m.reply_text(f"**Fail Reason »**\n<blockquote><i>{e}</i></blockquote>\n\n✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}🌟`")

    failed_count = 0
    count =int(raw_text)    
    arg = int(raw_text)
    
    processing_request = True
    try:
        for i in range(arg-1, len(links)):
            if cancel_requested:
                await m.reply_text("🚦**STOPPED**🚦")
                processing_request = False
                cancel_requested = False
                return
            

            Vxy = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = "https://" + Vxy
            link0 = "https://" + Vxy

            name1 = links[i][0].replace("(", "[").replace(")", "]").replace("_", "").replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").replace('"', '').strip()
            if "," in raw_text3:
                 name = f'{PRENAME} {name1[:60]}'
            else:
                 name = f'{name1[:60]}'
            


            if "acecwply" in url:
                cmd = f'yt-dlp -o "{name}.%(ext)s" -f "bestvideo[height<={raw_text2}]+bestaudio" --hls-prefer-ffmpeg --no-keep-video --remux-video mkv --no-warning "{url}"'

            elif "https://cpvideocdn.testbook.com/" in url or "https://cpvod.testbook.com/" in url:
                url = url.replace("https://cpvideocdn.testbook.com/","https://media-cdn.classplusapp.com/drm/")
                url = url.replace("https://cpvod.testbook.com/", "https://media-cdn.classplusapp.com/drm/")


                url = apis["API_DRM"] + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])
            
            elif any(x in url for x in ["static-trans-v1.classx.co.in","static-trans-v2.classx.co.in","static-trans-v1.appx.co.in","static-trans-v2.appx.co.in"]):
                base_with_params, sig = url.split("*")
                ext = ".mkv" if ".mkv" in base_with_params else ".mp4"
                base_clean = base_with_params.split(ext)[0] + ext
                base_clean = base_clean.replace("https://static-trans-v1.classx.co.in","https://appx-transcoded-videos-mcdn.akamai.net.in").replace("https://static-trans-v1.appx.co.in","https://appx-transcoded-videos-mcdn.akamai.net.in").replace("https://static-trans-v2.classx.co.in","https://transcoded-videos-v2.classx.co.in").replace("https://static-trans-v2.appx.co.in","https://transcoded-videos-v2.classx.co.in")
                url = f"{base_clean}*{sig}"

            
            elif "https://static-rec.classx.co.in/drm/" in url or "https://static-rec.appx.co.in/drm/" in url:
                base_with_params, signature = url.split("*")
                base_clean = base_with_params.split("?")[0]
                base_clean = base_clean.replace("https://static-rec.classx.co.in", "https://appx-recordings-mcdn.akamai.net.in")
                base_clean = base_clean.replace("https://static-rec.appx.co.in", "https://appx-recordings-mcdn.akamai.net.in")
                url = f"{base_clean}*{signature}"


            elif "https://static-wsb.classx.co.in/" in url or "https://static-wsb.appx.co.in/" in url:
                clean_url = url.split("?")[0]
                clean_url = clean_url.replace("https://static-wsb.classx.co.in", "https://appx-wsb-gcp-mcdn.akamai.net.in")
                clean_url = clean_url.replace("https://static-wsb.appx.co.in", "https://appx-wsb-gcp-mcdn.akamai.net.in")
                url = clean_url

            elif "https://static-db.classx.co.in/" in url or "https://static-db.appx.co.in/" in url:
                if "*" in url:
                    base_url, key = url.split("*", 1)
                    base_url = base_url.split("?")[0]
                    base_url = base_url.replace("https://static-db.classx.co.in", "https://appxcontent.kaxa.in")
                    base_url = base_url.replace("https://static-db.appx.co.in", "https://appxcontent.kaxa.in")
                    url = f"{base_url}*{key}"
                else:
                    base_url = url.split("?")[0]
                    url = base_url.replace("https://static-db.classx.co.in", "https://appxcontent.kaxa.in")
                    url = base_url.replace("https://static-db.appx.co.in", "https://appxcontent.kaxa.in")


            elif "https://static-db-v2.classx.co.in/" in url or "https://static-db-v2.appx.co.in/" in url:
                if "*" in url:
                    base_url, key = url.split("*", 1)
                    base_url = base_url.split("?")[0]
                    base_url = base_url.replace("https://static-db-v2.classx.co.in", "https://appx-content-v2.classx.co.in")
                    base_url = base_url.replace("https://static-db-v2.appx.co.in", "https://appx-content-v2.classx.co.in")
                    url = f"{base_url}*{key}"
                else:
                    base_url = url.split("?")[0]
                    url = base_url.replace("https://static-db-v2.classx.co.in", "https://appx-content-v2.classx.co.in")
                    url = base_url.replace("https://static-db-v2.appx.co.in", "https://appx-content-v2.classx.co.in")

            elif "classplusapp.com/drm/" in url:
                print("\n🔐 Fetching DRM keys...")
                api_url = apis["API_DRM"] + url
                max_retries = 2  # Reduced retries
                retry_count = 0

                while retry_count < max_retries:
                    try:
                        retry_count += 1
                        mpd, keys = helper.get_mps_and_keys(api_url)

                        if mpd and keys:
                            url = mpd
                            keys_string = " ".join([f"--key {key}" for key in keys])
                            print("✅ DRM keys fetched!")
                            break
                        
                        print(f"⚠️ Retry {retry_count}/{max_retries}...")
                        await asyncio.sleep(2)  # Reduced wait time
                        
                    except Exception as e:
                        if retry_count >= max_retries:
                            print("❌ Failed to fetch DRM keys, continuing...")
                            break
                        print(f"⚠️ Retry {retry_count}/{max_retries}...")
                        await asyncio.sleep(2)  # Reduced wait time

            elif 'media-cdn.classplusapp.com' in url or 'media-cdn-alisg.classplusapp.com' in url or 'media-cdn-a.classplusapp.com' in url or 'videos.classplusapp' in url or 'tencdn.classplusapp' in url: 
                if 'm3u8' in url:
                    print(f"Processing Classplus URL: {url}")
                    max_retries = 3  # Maximum number of retries
                    retry_count = 0
                    success = False
                    
                    # Check if raw_text4 is a valid JWT token (has 2 dots and longer than 30 chars)
                    is_valid_token = raw_text4 and raw_text4 != "/d" and raw_text4.count('.') == 2 and len(raw_text4) > 30
                    
                    while not success and retry_count < max_retries:
                        try:
                            # Only add token if it's valid JWT
                            params = {"url": url}
                            if is_valid_token:
                                params["token"] = raw_text4
                                print("Using provided JWT token")
                            
                            # First try with direct URL
                            response = requests.get(apis["API_CLASSPLUS"], params=params)
                            
                            if response.status_code == 200:
                                try:
                                    res_json = response.json()
                                    url = res_json.get("data", {}).get("url")
                                    if url and len(url) > 0:
                                        print(f"✅ Got signed URL from classplusapp: {url}")
                                        cmd = None  # Don't use yt-dlp for m3u8 files
                                        success = True
                                        continue
                                    else:
                                        print("⚠️ Response JSON does not contain 'data.url'. Here's full response:")
                                        print(json.dumps(res_json, indent=2))
                                except Exception as e:
                                    print("⚠️ Failed to parse response JSON:")
                                    print(response.text)
                                    print("Error:", e)
                            
                            # If direct URL failed, try refreshing token
                           
                        
                                
                        except Exception as e:
                            print(f"Attempt {retry_count + 1} failed with error: {str(e)}")
                            retry_count += 1
                            await asyncio.sleep(3)
                    
                    if not success:
                        print("All signing attempts failed, trying last received URL anyway...")

            elif "childId" in url and "parentId" in url:
                api_base = json.load(open("api.json"))["PW_API"]
                url = f"{api_base}/pw?url={url}&token={raw_text4}"

            elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                api_base = json.load(open("api.json"))["PW_API"]
                url = f"{api_base}/pw?url={url}&token={raw_text4}"

            if ".pdf*" in url:
                url = url.split("*")[0]  # keep only PDF url before '*'

            
            #PREMIUM URLS
            elif "https://b7ql8e5g.fs-vid.com" in url:
                cmd = f'yt-dlp --add-header "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36" --add-header "Referer: https://cl4.jinc-jodhpur.com/" -f "{ytf}" "{url}" -o "{name}.mp4"'

            elif "vz-8ed22225-59e.b-cdn.net" in url or ".b-cdn.net" in url:
                cmd = f'yt-dlp --referer "https://player.filecdn.in" --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36" --output "{name}.mp4" --no-mtime --restrict-filenames --no-playlist --compat-options filename "{url}"'

            elif "https://i.filecdn.in" in url and url.endswith(".pdf"):
                cmd = f'yt-dlp --add-header "user-agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64)" --add-header "referer:https://player.filecdn.in" "{url}" -o "{name}.pdf"'


            elif 'encrypted.m' in url:
                appxkey = url.split('*')[1]
                url = url.split('*')[0]

            if "youtu" in url:
                ytf = f"bv*[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[height<=?{raw_text2}]"
            elif "embed" in url:
                ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
           
            if "jw-prod" in url:
                url = url.replace("https://apps-s3-jw-prod.utkarshapp.com/admin_v1/file_library/videos","https://d1q5ugnejk3zoi.cloudfront.net/ut-production-jw/admin_v1/file_library/videos")
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            elif "webvideos.classplusapp." in url:
               cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}".mp4'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:
                if raw_text5 == "yes":
                    raw_title = links[i][0]

                    # Try to find the first occurrence of bracketed text (e.g., [..] or (..))
                    t_match = re.search(r"[\(\[]([^\)\]]+)[\)\]]", raw_title)

                    if t_match:
                        # Extract text inside brackets
                        t_name = t_match.group(1).strip()

                        # Remove only the matched bracketed part from raw_title
                        start, end = t_match.span()
                        v_name = (raw_title[:start] + raw_title[end:]).strip()
                    else:
                        t_name = "Untitled"
                        v_name = raw_title.strip()

                    # Clean: remove everything after the last colon,
                    # and strip any trailing - : | _ – —
                    v_name = re.sub(r"[-:|–—_\s]*https?.*", "", v_name).strip()


                    cc = f'🏷️ Fɪʟᴇ ID : {str(count).zfill(3)}  ─────\n\n🎥 **ᴛɪᴛʟᴇ** :{v_name}.mp4\n\n<blockquote><b>📚 **𝗕ᴀᴛᴄʜ** : {b_name}\n\n📝 **ᴛᴏᴘɪᴄ** : {t_name}</b></blockquote>\n\n📥 ᴇxᴛʀᴀᴄᴛᴇᴅ ʙʏ ➤ {CR}\n'
                    cc1 = f'───── PDF ID : {str(count).zfill(3)} ─────\n\n📑 **ᴛɪᴛʟᴇ** :{v_name} .pdf\n\n<blockquote><b>📚 **𝗕ᴀᴛᴄʜ** : {b_name}\n\n📝 **ᴛᴏᴘɪᴄ** : {t_name}</b></blockquote>\n\n📥 ᴇxᴛʀᴀᴄᴛᴇᴅ ʙʏ ➤ {CR}\n'
                    cczip = f'─────  Zip Id : {str(count).zfill(3)}  ─────\n\n📁 **ᴛɪᴛʟᴇ** :{v_name} .zip\n\n<blockquote><b>📚 **𝗕ᴀᴛᴄʜ** : {b_name}\n\n📝 **ᴛᴏᴘɪᴄ** : {t_name}</b></blockquote>\n\n📥 ᴇxᴛʀᴀᴄᴛᴇᴅ ʙʏ ➤ {CR}\n'
                    ccimg = f'─────  Img Id : {str(count).zfill(3)}  ─────\n\n🖼️ **ᴛɪᴛʟᴇ** :{v_name} .jpg\n\n<blockquote><b>📚 **𝗕ᴀᴛᴄʜ** : {b_name}\n\n📝 **ᴛᴏᴘɪᴄ** : {t_name}</b></blockquote>\n\n📥 ᴇxᴛʀᴀᴄᴛᴇᴅ ʙʏ ➤ {CR}\n'
                    cchtml = f'─────  Html Id : {str(count).zfill(3)}  ─────\n\n🌐 **ᴛɪᴛʟᴇ** :{v_name} .html\n\n<blockquote><b>📚 **𝗕ᴀᴛᴄʜ** : {b_name}\n\n📝 **ᴛᴏᴘɪᴄ** : {t_name}</b></blockquote>\n\n📥 ᴇxᴛʀᴀᴄᴛᴇᴅ ʙʏ ➤ {CR}\n'
                    ccyt = f'─────  VID ID : {str(count).zfill(3)}  ─────\n\n🎥 **ᴛɪᴛʟᴇ** :{v_name} .mp4\n\n<a href="{url}">__**Click Here to Watch Stream**__</a>\n<blockquote><b>💠 **ʙᴀᴛᴄʜ** : {b_name}\n\n📝 **ᴛᴏᴘɪᴄ** : {t_name}</b></blockquote>\n\n📥 ᴇxᴛʀᴀᴄᴛᴇᴅ ʙʏ ➤ {CR}\n'


                else:
                    cc = f'🏷️ **Fɪʟᴇ ID : {str(count).zfill(3)}** \n\n🎞️ **Tɪᴛʟᴇ :** {name1} [{res}p] .mp4\n\n<blockquote><b>📚 **𝗕ᴀᴛᴄʜ** :</b> {b_name}</blockquote>\n\n🎓 **Exᴛʀᴀᴄᴛ Bʏ ➤ {CR}**\n'
                    cc1 = f'🏷️ **Fɪʟᴇ ID : {str(count).zfill(3)}** \n\n📝 **Tɪᴛʟᴇ :** {name1} .pdf\n\n<blockquote><b>📚 **𝗕ᴀᴛᴄʜ** :</b> {b_name}</blockquote>\n\n🎓 **Exᴛʀᴀᴄᴛ Bʏ ➤ {CR}**\n'
                    cczip = f'🏷️ **Fɪʟᴇ ID : {str(count).zfill(3)}** \n\n💾 **Tɪᴛʟᴇ :** {name1} .zip\n\n<blockquote><b>📚 **𝗕ᴀᴛᴄʜ** :</b> {b_name}</blockquote>\n\n**🎓 Exᴛʀᴀᴄᴛ Bʏ ➤ {CR}**\n'
                    ccimg = f'🏷️ **Fɪʟᴇ ID : {str(count).zfill(3)}** \n\n🖼️ **Tɪᴛʟᴇ :** {name1} .jpg\n\n<blockquote><b>📚 **𝗕ᴀᴛᴄʜ** :</b> {b_name}</blockquote>\n\n**🎓 Exᴛʀᴀᴄᴛ Bʏ ➤ {CR}**\n'
                    ccm = f'🏷️ **Fɪʟᴇ ID : {str(count).zfill(3)}** \n\n🎵 **Tɪᴛʟᴇ :** {name1} .mp3\n\n<blockquote><b>📚 **𝗕ᴀᴛᴄʜ** :</b> {b_name}</blockquote>\n\n**🎓 Exᴛʀᴀᴄᴛ Bʏ➤ {CR}**\n'
                    cchtml = f'🏷️ **Fɪʟᴇ ID : {str(count).zfill(3)}** \n\n🌐 **Tɪᴛʟᴇ :** {name1} .html\n\n<blockquote><b>📚 **𝗕ᴀᴛᴄʜ** :</b> {b_name}</blockquote>\n\n**🎓 Exᴛʀᴀᴄᴛ Bʏ ➤ {CR}**\n'
          
                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=channel_id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue    
  
                elif ".pdf" in url:
                    if "cwmediabkt99" in url:
                        max_retries = 3  # Define the maximum number of retries
                        retry_delay = 4  # Delay between retries in seconds
                        success = False  # To track whether the download was successful
                        failure_msgs = []  # To keep track of failure messages
                        
                        for attempt in range(max_retries):
                            try:
                                await asyncio.sleep(retry_delay)
                                url = url.replace(" ", "%20")
                                scraper = cloudscraper.create_scraper()
                                response = scraper.get(url)

                                if response.status_code == 200:
                                    with open(f'{name}.pdf', 'wb') as file:
                                        file.write(response.content)
                                    await asyncio.sleep(retry_delay)  # Optional, to prevent spamming
                                    copy = await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1)
                                    count += 1
                                    os.remove(f'{name}.pdf')
                                    success = True
                                    break  # Exit the retry loop if successful
                                else:
                                    failure_msg = await m.reply_text(f"Attempt {attempt + 1}/{max_retries} failed: {response.status_code} {response.reason}")
                                    failure_msgs.append(failure_msg)
                                    
                            except Exception as e:
                                failure_msg = await m.reply_text(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                                failure_msgs.append(failure_msg)
                                await asyncio.sleep(retry_delay)
                                continue 
                        for msg in failure_msgs:
                            await msg.delete()
                            
                    else:
                        try:
                            cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                            download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                            os.system(download_cmd)
                            copy = await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1)
                            count += 1
                            os.remove(f'{name}.pdf')
                        except FloodWait as e:
                            await m.reply_text(str(e))
                            time.sleep(e.x)
                            continue    

                elif ".ws" in url and  url.endswith(".ws"):
                    try:
                        await helper.pdf_download(f"{api_url}utkash-ws?url={url}&authorization={api_token}",f"{name}.html")
                        time.sleep(1)
                        await bot.send_document(chat_id=channel_id, document=f"{name}.html", caption=cchtml)
                        os.remove(f'{name}.html')
                        count += 1
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue    
                            
                elif any(ext in url for ext in [".jpg", ".jpeg", ".png"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_photo(chat_id=channel_id, photo=f'{name}.{ext}', caption=ccimg)
                        count += 1
                        os.remove(f'{name}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue    

                elif any(ext in url for ext in [".mp3", ".wav", ".m4a"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -x --audio-format {ext} -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        await bot.send_document(chat_id=channel_id, document=f'{name}.{ext}', caption=cc1)
                        os.remove(f'{name}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue    
                    
                elif 'encrypted.m' in url:    
                    Show = (
    "**⏳ ᴘʀᴏᴄᴇꜱꜱɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ ⏳**\n"
    f"➤ {str(count).zfill(3)} __{name1}__"
)
                    prog = await bot.send_message(channel_id, Show, disable_web_page_preview=True)
                    try:

                        res_file = await helper.download_and_decrypt_video(url, cmd, name, appxkey)  
                        filename = res_file  
                        await prog.delete(True) 
                        if os.path.exists(filename):
                            sent_msg = await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id, watermark=watermark)
                            if raw_text5 == "yes":
                                topic_title = t_name if 't_name' in locals() else None
                                if topic_title and topic_title not in topic_first_message_links and sent_msg is not None:
                                    link = _build_msg_link(chat_obj, sent_msg.id)
                                    if link:
                                        topic_first_message_links[topic_title] = link
                                        try:
                                            db.add_topic_index(m.from_user.id, bot_username, channel_id, b_name, topic_title, link)
                                        except Exception:
                                            pass
                            count += 1
                        else:
                            error_msg = (
                            "⚠️ ᴅᴏᴡɴʟᴏᴀᴅ ғᴀɪʟᴇᴅ ⚠️\n"
                            f"📛 ɴᴀᴍᴇ  : `{str(count).zfill(3)} {name1}`\n"
                            f"🔗 ᴜʀʟ    : {link0}\n"
                            f"❗ ʀᴇᴀꜱᴏɴ : {str(e)}"
                        )
                            await bot.send_message(channel_id, error_msg, disable_web_page_preview=True)
                            count += 1
                            failed_count += 1
                            await asyncio.sleep(2)  # avoid flood wait
                            continue
                        
                        
                    except Exception as e:
                        error_msg = (
                            "⚠️ ᴅᴏᴡɴʟᴏᴀᴅ ғᴀɪʟᴇᴅ ⚠️\n"
                            f"📛 ɴᴀᴍᴇ  : `{str(count).zfill(3)} {name1}`\n"
                            f"🔗 ᴜʀʟ    : {link0}\n"
                            f"❗ ʀᴇᴀꜱᴏɴ : {str(e)}"
                        )
                        await bot.send_message(channel_id, error_msg, disable_web_page_preview=True)
                        count += 1
                        failed_count += 1
                        await asyncio.sleep(2)  # avoid flood wait
                        continue
                    

                elif 'drmcdni' in url or 'drm/wv' in url:
                    Show = (
    "**⏳ ᴘʀᴏᴄᴇꜱꜱɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ ⏳**\n"
    f"➤ {str(count).zfill(3)} __{name1}__"
                    )
                    prog = await bot.send_message(channel_id, Show, disable_web_page_preview=True)
                    res_file = await helper.decrypt_and_merge_video(mpd, keys_string, path, name, raw_text2)
                    filename = res_file
                    await prog.delete(True)
                    sent_msg = await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id, watermark=watermark)
                    if raw_text5 == "yes":
                        topic_title = t_name if 't_name' in locals() else None
                        if topic_title and topic_title not in topic_first_message_links and sent_msg is not None:
                            link = _build_msg_link(chat_obj, sent_msg.id)
                            if link:
                                topic_first_message_links[topic_title] = link
                                try:
                                    db.add_topic_index(m.from_user.id, bot_username, channel_id, b_name, topic_title, link)
                                except Exception:
                                    pass
                    count += 1
                    await asyncio.sleep(1)
                    continue
     
             

             
                else:
                    Show = (
    "**⏳ ᴘʀᴏᴄᴇꜱꜱɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ ⏳**\n"
    f"➤ {str(count).zfill(3)} __{name1}__"
)
                    prog = await bot.send_message(channel_id, Show, disable_web_page_preview=True)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    sent_msg = await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id, watermark=watermark)
                    if raw_text5 == "yes":
                        topic_title = t_name if 't_name' in locals() else None
                        if topic_title and topic_title not in topic_first_message_links and sent_msg is not None:
                            link = _build_msg_link(chat_obj, sent_msg.id)
                            if link:
                                topic_first_message_links[topic_title] = link
                                try:
                                    db.add_topic_index(m.from_user.id, bot_username, channel_id, b_name, topic_title, link)
                                except Exception:
                                    pass
                    count += 1
                    time.sleep(1)
                
            except Exception as e:
                error_msg = (
                    "⚠️ ᴅᴏᴡɴʟᴏᴀᴅ ғᴀɪʟᴇᴅ ⚠️\n"
                    f"📛 ɴᴀᴍᴇ  : `{str(count).zfill(3)} {name1}`\n"
                    f"🔗 ᴜʀʟ    : {link0}\n"
                    f"❗ ʀᴇᴀꜱᴏɴ : {str(e)}"
                )
                await bot.send_message(channel_id, error_msg, disable_web_page_preview=True)
                count += 1
                failed_count += 1
                await asyncio.sleep(2)  # avoid flood wait
                continue

    except Exception as e:
        await m.reply_text(e)
        time.sleep(2)

    success_count = len(links) - failed_count
    video_count = v2_count + mpd_count + m3u8_count + yt_count + drm_count + zip_count + other_count
    # Build Topic Index if topic-wise uploader was enabled
    if raw_text5 == "yes" and len(topic_first_message_links) > 0:
        index_lines = []
        index_lines.append(f"📚 <b>{to_small_caps('INDEX')}</b>")
        index_lines.append("──────────────────────────")

        for topic, link in topic_first_message_links.items():
            small_topic = to_small_caps(topic)
            # Topic name ko clickable banaya
            line = f"➤ <a href=\"{link}\">{small_topic}</a>\n"
            index_lines.append(line)

        try:
            await bot.send_message(
                channel_id, 
                "\n".join(index_lines), 
                disable_web_page_preview=True            )
        except Exception:
            pass

    processing_request = False
    if raw_text7 == "/d":
        await bot.send_message(
        channel_id,
        (
            "✨ ᴅᴏɴᴇ ᴡɪᴛʜ ᴘʀᴏᴄᴇꜱꜱ\n\n"
            f"📌 ʙᴀᴛᴄʜ : {b_name}\n"
            f"🔗 ᴛᴏᴛᴀʟ ᴜʀʟꜱ : {len(links)}\n"
            f"🟢 ꜱᴜᴄᴄᴇꜱꜱ : {success_count}\n"
            f"❌ ꜰᴀɪʟᴇᴅ : {failed_count}\n\n"
            f"➤ ᴠɪᴅᴇᴏꜱ : {video_count}\n"
            f"➤ ᴘᴅꜰꜱ : {pdf_count}\n"
            f"➤ ɪᴍᴀɢᴇꜱ : {img_count}\n\n"
        )
    )

    else:
        await bot.send_message(
    channel_id,
    f"<b>{b_name} ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ</b>\n"
    f"🔴 <b>ꜰᴀɪʟᴇᴅ ᴜʀʟꜱ:</b> {failed_count}\n"
    f"🟢 <b>sᴜᴄᴄᴇꜱꜱꜰᴜʟ ᴜʀʟꜱ:</b> {success_count}\n\n"
    f"➤ ᴠɪᴅᴇᴏꜱ : {video_count}\n"
    f"➤ ᴘᴅꜰꜱ : {pdf_count}\n"
    f"➤ ɪᴍᴀɢᴇꜱ : {img_count}")

        await bot.send_message(
        m.chat.id,
    f"✅ ᴛᴀꜱᴋ ᴄᴏᴍᴘʟᴇᴛᴇᴅ! ᴘʟᴇᴀꜱᴇ ᴄʜᴇᴄᴋ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ."
)




@bot.on_message(filters.text & filters.private  & auth_filter)
async def text_handler(bot: Client, m: Message):
    if m.from_user.is_bot:
        return
    links = m.text
    path = None
    match = re.search(r'https?://\S+', links)
    if match:
        link = match.group(0)
    else:
        await m.reply_text("<pre><code>Invalid link format.</code></pre>")
        return
        
    editable = await m.reply_text(f"<pre><code>**🔹Processing your link...\n🔁Please wait...⏳**</code></pre>")
    await m.delete()

    await editable.edit(f"╭━━━━❰ᴇɴᴛᴇʀ ʀᴇꜱᴏʟᴜᴛɪᴏɴ❱━━➣ \n┣━━⪼ send `144`  for 144p\n┣━━⪼ send `240`  for 240p\n┣━━⪼ send `360`  for 360p\n┣━━⪼ send `480`  for 480p\n┣━━⪼ send `720`  for 720p\n┣━━⪼ send `1080` for 1080p\n╰━━⌈⚡[`{CREDIT}`]⚡⌋━━➣ ")
    input2: Message = await bot.listen(editable.chat.id, filters=filters.text & filters.user(m.from_user.id))
    raw_text2 = input2.text
    quality = f"{raw_text2}p"
    await input2.delete(True)
    try:
        if raw_text2 == "144":
            res = "256x144"
        elif raw_text2 == "240":
            res = "426x240"
        elif raw_text2 == "360":
            res = "640x360"
        elif raw_text2 == "480":
            res = "854x480"
        elif raw_text2 == "720":
            res = "1280x720"
        elif raw_text2 == "1080":
            res = "1920x1080" 
        else: 
            res = "UN"
    except Exception:
            res = "UN"
          
   
    raw_text4 = "working_token"
    thumb = "/d"
    count =0
    arg =1
    channel_id = m.chat.id
    try:
            Vxy = link.replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = Vxy


            name1 = links.replace("(", "[").replace(")", "]").replace("_", "").replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").replace('"', '').strip()
            name = f'{name1[:60]}'
            

            if "acecwply" in url:
                cmd = f'yt-dlp -o "{name}.%(ext)s" -f "bestvideo[height<={raw_text2}]+bestaudio" --hls-prefer-ffmpeg --no-keep-video --remux-video mkv --no-warning "{url}"'

            elif "https://cpvod.testbook.com/" in url:
                url = url.replace("https://cpvod.testbook.com/","https://media-cdn.classplusapp.com/drm/")
                url = apis["API_DRM"] + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            elif "https://static-trans-v1.classx.co.in" in url or "https://static-trans-v2.classx.co.in" in url:
                base_with_params, signature = url.split("*")

                base_clean = base_with_params.split(".mkv")[0] + ".mkv"

                if "static-trans-v1.classx.co.in" in url:
                    base_clean = base_clean.replace("https://static-trans-v1.classx.co.in", "https://appx-transcoded-videos-mcdn.akamai.net.in")
                elif "static-trans-v2.classx.co.in" in url:
                    base_clean = base_clean.replace("https://static-trans-v2.classx.co.in", "https://transcoded-videos-v2.classx.co.in")

                url = f"{base_clean}*{signature}"
            
            elif "https://static-rec.classx.co.in/drm/" in url:
                base_with_params, signature = url.split("*")

                base_clean = base_with_params.split("?")[0]

                base_clean = base_clean.replace("https://static-rec.classx.co.in", "https://appx-recordings-mcdn.akamai.net.in")

                url = f"{base_clean}*{signature}"

            elif "https://static-wsb.classx.co.in/" in url:
                clean_url = url.split("?")[0]

                clean_url = clean_url.replace("https://static-wsb.classx.co.in", "https://appx-wsb-gcp-mcdn.akamai.net.in")

                url = clean_url

            elif "https://static-db.classx.co.in/" in url:
                if "*" in url:
                    base_url, key = url.split("*", 1)
                    base_url = base_url.split("?")[0]
                    base_url = base_url.replace("https://static-db.classx.co.in", "https://appxcontent.kaxa.in")
                    url = f"{base_url}*{key}"
                else:
                    base_url = url.split("?")[0]
                    url = base_url.replace("https://static-db.classx.co.in", "https://appxcontent.kaxa.in")


            elif "https://static-db-v2.classx.co.in/" in url:
                if "*" in url:
                    base_url, key = url.split("*", 1)
                    base_url = base_url.split("?")[0]
                    base_url = base_url.replace("https://static-db-v2.classx.co.in", "https://appx-content-v2.classx.co.in")
                    url = f"{base_url}*{key}"
                else:
                    base_url = url.split("?")[0]
                    url = base_url.replace("https://static-db-v2.classx.co.in", "https://appx-content-v2.classx.co.in")

          


            elif "classplusapp.com/drm/" in url:
                print("\n🔐 Fetching DRM keys...")
                api_url = apis["API_DRM"] + url
                max_retries = 2  # Reduced retries
                retry_count = 0

                while retry_count < max_retries:
                    try:
                        retry_count += 1
                        mpd, keys = helper.get_mps_and_keys(api_url)

                        if mpd and keys:
                            url = mpd
                            keys_string = " ".join([f"--key {key}" for key in keys])
                            print("✅ DRM keys fetched!")
                            break
                        
                        print(f"⚠️ Retry {retry_count}/{max_retries}...")
                        await asyncio.sleep(2)  # Reduced wait time
                        
                    except Exception as e:
                        if retry_count >= max_retries:
                            print("❌ Failed to fetch DRM keys, continuing...")
                            break
                        print(f"⚠️ Retry {retry_count}/{max_retries}...")
                        await asyncio.sleep(2)  # Reduced wait time


            elif 'media-cdn.classplusapp.com' in url or 'media-cdn-alisg.classplusapp.com' in url or 'media-cdn-a.classplusapp.com' in url or 'videos.classplusapp' in url or 'tencdn.classplusapp' in url: 
                if 'master.m3u8' in url:
                    print(f"Processing Classplus URL: {url}")
                    max_retries = 3  # Maximum number of retries
                    retry_count = 0
                    success = False
                    
                    # Check if raw_text4 is a valid JWT token (has 2 dots and longer than 30 chars)
                    is_valid_token = raw_text4 and raw_text4 != "/d" and raw_text4.count('.') == 2 and len(raw_text4) > 30
                    
                    while not success and retry_count < max_retries:
                        try:
                            # Only add token if it's valid JWT
                            params = {"url": url}
                            if is_valid_token:
                                params["token"] = raw_text4
                                print("Using provided JWT token")
                            
                            # First try with direct URL
                            response = requests.get(apis["API_CLASSPLUS"], params=params)
                            
                            if response.status_code == 200:
                                try:
                                    res_json = response.json()
                                    url = res_json.get("data", {}).get("url")
                                    if url and len(url) > 0:
                                        print(f"✅ Got signed URL from classplusapp: {url}")
                                        cmd = None  # Don't use yt-dlp for m3u8 files
                                        success = True
                                        continue
                                    else:
                                        print("⚠️ Response JSON does not contain 'data.url'. Here's full response:")
                                        print(json.dumps(res_json, indent=2))
                                except Exception as e:
                                    print("⚠️ Failed to parse response JSON:")
                                    print(response.text)
                                    print("Error:", e)
                        
                            # If direct URL failed, try refreshing token
                            print(f"Attempt {retry_count + 1} failed with status {response.status_code}")
                            
                           
                            
                        except Exception as e:
                            print(f"Attempt {retry_count + 1} failed with error: {str(e)}")
                            retry_count += 1
                            await asyncio.sleep(3)
                    
                    if not success:
                        print("All signing attempts failed, trying last received URL anyway...")

            elif "childId" in url and "parentId" in url:
                    url = f"https://anonymousrajputplayer-9ab2f2730a02.herokuapp.com/pw?url={url}&token={raw_text4}"
                           
            elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                url = f"https://anonymouspwplayer-b99f57957198.herokuapp.com/pw?url={url}?token={raw_text4}"

            elif "https://i.filecdn.in" in url and url.endswith(".pdf"):
                cmd = f'yt-dlp --add-header "user-agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64)" --add-header "referer:https://player.filecdn.in" "{url}" -o "{name}.pdf"'


            if ".pdf*" in url:
                url = f"https://dragoapi.vercel.app/pdf/{url}"
            
            elif 'encrypted.m' in url:
                appxkey = url.split('*')[1]
                url = url.split('*')[0]

            if "youtu" in url:
                ytf = f"bv*[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[height<=?{raw_text2}]"
            elif "embed" in url:
                ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
           
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            elif "webvideos.classplusapp." in url:
               cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:
                cc = f'🎥𝐓𝐢𝐭𝐥𝐞 » `{name} [{res}].mp4`\n\n🔗𝐋𝐢𝐧𝐤 » <a href="{link}">__**CLICK HERE**__</a>\n\n🌟𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 » `{CREDIT}`'
                cc1 = f'📑𝐓𝐢𝐭𝐥𝐞 » `{name}`\n\n🔗𝐋𝐢𝐧𝐤 » <a href="{link}">__**CLICK HERE**__</a>\n\n🌟𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 » `{CREDIT}`'
                  
                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=m.chat.id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        pass

                elif ".pdf" in url:
                    if "cwmediabkt99" in url:
                        max_retries = 15  # Define the maximum number of retries
                        retry_delay = 4  # Delay between retries in seconds
                        success = False  # To track whether the download was successful
                        failure_msgs = []  # To keep track of failure messages
                        
                        for attempt in range(max_retries):
                            try:
                                await asyncio.sleep(retry_delay)
                                url = url.replace(" ", "%20")
                                scraper = cloudscraper.create_scraper()
                                response = scraper.get(url)

                                if response.status_code == 200:
                                    with open(f'{name}.pdf', 'wb') as file:
                                        file.write(response.content)
                                    await asyncio.sleep(retry_delay)  # Optional, to prevent spamming
                                    copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                                    os.remove(f'{name}.pdf')
                                    success = True
                                    break  # Exit the retry loop if successful
                                else:
                                    failure_msg = await m.reply_text(f"Attempt {attempt + 1}/{max_retries} failed: {response.status_code} {response.reason}")
                                    failure_msgs.append(failure_msg)
                                    
                            except Exception as e:
                                failure_msg = await m.reply_text(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                                failure_msgs.append(failure_msg)
                                await asyncio.sleep(retry_delay)
                                continue 

                        # Delete all failure messages if the PDF is successfully downloaded
                        for msg in failure_msgs:
                            await msg.delete()
                            
                        if not success:
                            # Send the final failure message if all retries fail
                            await m.reply_text(f"Failed to download PDF after {max_retries} attempts.\n⚠️**Downloading Failed**⚠️\n**Name** =>> {str(count).zfill(3)} {name1}\n**Url** =>> {link0}", disable_web_page_preview)
                            
                    else:
                        try:
                            cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                            download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                            os.system(download_cmd)
                            copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                            os.remove(f'{name}.pdf')
                        except FloodWait as e:
                            await m.reply_text(str(e))
                            time.sleep(e.x)
                            pass   

                elif any(ext in url for ext in [".mp3", ".wav", ".m4a"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -x --audio-format {ext} -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        await bot.send_document(chat_id=m.chat.id, document=f'{name}.{ext}', caption=cc1)
                        os.remove(f'{name}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        pass

                elif any(ext in url for ext in [".jpg", ".jpeg", ".png"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_photo(chat_id=m.chat.id, photo=f'{name}.{ext}', caption=cc1)
                        count += 1
                        os.remove(f'{name}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        pass
                                
                elif 'encrypted.m' in url:    
                    Show = f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳**\n" \
                           f"🔗𝐋𝐢𝐧𝐤 » {url}\n" \
                           f"✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}"
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.download_and_decrypt_video(url, cmd, name, appxkey)  
                    filename = res_file  
                    await prog.delete(True)  
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id, watermark=watermark)
                    await asyncio.sleep(1)  
                    pass

                elif 'drmcdni' in url or 'drm/wv' in url:
                    Show = f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳**\n" \
                           f"🔗𝐋𝐢𝐧𝐤 » {url}\n" \
                           f"✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}"
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.decrypt_and_merge_video(mpd, keys_string, path, name, raw_text2)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id, watermark=watermark)
                    await asyncio.sleep(1)
                    pass

                else:
                    Show = f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳**\n" \
                           f"🔗𝐋𝐢𝐧𝐤 » {url}\n" \
                           f"✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}"
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id, watermark=watermark)
                    time.sleep(1)
                
            except Exception as e:
                    await m.reply_text(f"⚠️𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 𝐈𝐧𝐭𝐞𝐫𝐮𝐩𝐭𝐞𝐝\n\n🔗𝐋𝐢𝐧𝐤 » `{link}`\n\n<blockquote><b><i>⚠️Failed Reason »**__\n{str(e)}</i></b></blockquote>")
                    pass

    except Exception as e:
        await m.reply_text(str(e))

def notify_owner():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": OWNER_ID,
        "text": "BOT is Live Now 🤖\n\n📝 Send /drm & Choose Quality\n😎 Aur Maze kro"
    }
    requests.post(url, data=data)


def reset_and_set_commands():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
    # Reset
    requests.post(url, json={"commands": []})
    # Set new
    commands = [
    {"command": "start", "description": "✅ ᴄʜᴇᴄᴋ ɪꜰ ᴛʜᴇ ʙᴏᴛ ɪꜱ ᴀʟɪᴠᴇ"},
    {"command": "drm", "description": "📄 ᴜᴘʟᴏᴀᴅ ᴀ .ᴛxᴛ ꜰɪʟᴇ"},
    {"command": "stop", "description": "⏹ ᴛᴇʀᴍɪɴᴀᴛᴇ ᴛʜᴇ ᴏɴɢᴏɪɴɢ ᴘʀᴏᴄᴇꜱꜱ"},
    {"command": "reset", "description": "♻️ ʀᴇꜱᴇᴛ ᴛʜᴇ ʙᴏᴛ"},
    {"command": "cookies", "description": "🍪 ᴜᴘʟᴏᴀᴅ ʏᴏᴜᴛᴜʙᴇ ᴄᴏᴏᴋɪᴇꜱ"},
    {"command": "t2t", "description": "📝 ᴛᴇxᴛ → .ᴛxᴛ ɢᴇɴᴇʀᴀᴛᴏʀ"},
    {"command": "id", "description": "🆔 ɢᴇᴛ ʏᴏᴜʀ ᴜꜱᴇʀ ɪᴅ"},
    {"command": "logs", "description": "👁️ ᴠɪᴇᴡ ʙᴏᴛ ᴀᴄᴛɪᴠɪᴛʏ"},
    {"command": "plan", "description": "⏸ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ"},
]

    requests.post(url, json={"commands": commands})
    



if __name__ == "__main__":
    reset_and_set_commands()
    notify_owner() 

bot.run()
