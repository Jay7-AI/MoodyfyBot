bot.py

import os import requests import random from pyrogram import Client, filters from pyrogram.types import Message from pytgcalls import PyTgCalls, idle from pytgcalls.types.input_stream import InputStream, InputAudioStream import yt_dlp

Load environment variables

from dotenv import load_dotenv load_dotenv()

API_ID = int(os.getenv("API_ID")) API_HASH = os.getenv("API_HASH") BOT_TOKEN = os.getenv("BOT_TOKEN") GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

Initialize Bot and Voice Client

app = Client("moodyfy", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN) pytgcalls = PyTgCalls(app)

Directories

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "./downloads") os.makedirs(DOWNLOAD_DIR, exist_ok=True)

Flirty auto replies

FLIRTY_KEYWORDS = ["moody", "kya kar", "zinda", "sun rahe", "idhar"] FLIRTY_LINES = [ "Aapko yaad kr rha tha cutie 🥰😘", "Itna mat satao na... sharma jaata hoon 😳💕", "Tum bulao... aur main naa aau? 😍", "Bas music baja raha hoon... dil se 💖", "Tumhare bina to playlist bhi adhoori lagti hai 😔🎧" ]

Mood-based playlists

MOOD_SONGS = { "sad": ["https://youtu.be/abcd", "https://youtu.be/def"], "happy": ["https://youtu.be/xyz", "https://youtu.be/uvw"], # add more moods }

Download audio util

def download_audio(url: str) -> (str, str): opts = { 'format': 'bestaudio/best', 'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s', 'quiet': True, 'postprocessors': [{ 'key': 'FFmpegExtractAudio', 'preferredcodec': 'opus', 'preferredquality': '64', }], } with yt_dlp.YoutubeDL(opts) as ydl: info = ydl.extract_info(url, download=True) title = info.get('title', 'Unknown') filepath = ydl.prepare_filename(info).rsplit('.', 1)[0] + ".opus" return filepath, title

Ask Gemini

def ask_gemini(query: str) -> str: url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}" headers = {'Content-Type': 'application/json'} data = {"contents": [{"parts": [{"text": query}]}]} res = requests.post(url, headers=headers, json=data) if res.status_code == 200: return res.json()['candidates'][0]['content']['parts'][0]['text'] return "Kuch samajh nahi aaya, try again."

Handlers

@app.on_message(filters.command("start")) async def start(_, message: Message): await message.reply("👋 Welcome to Moodyfy Bot! Use /help to see commands.")

@app.on_message(filters.command("help")) async def help_cmd(_, message: Message): text = ( "📜 Moodyfy Commands:\n" "/play <name|link> - Play music in VC\n" "/vplay <name|link> - Play video in VC\n" "/skip, /pause, /resume, /end - VC controls\n" "/ai <text> - AI mood-based reply\n" "\nJust ask casually: 'Moody kya kar rha hai?' for flirty auto replies!") await message.reply(text)

@app.on_message(filters.text & filters.group) async def flirty_reply(client, message: Message): txt = message.text.lower() if any(k in txt for k in FLIRTY_KEYWORDS): await message.reply(random.choice(FLIRTY_LINES))

@app.on_message(filters.command("ai") & filters.group) async def ai_reply(_, message: Message): query = message.text.split(None, 1)[1] if len(message.command) > 1 else "Mood batao" reply = ask_gemini(query) await message.reply(reply)

@app.on_message(filters.command("play") & filters.group) async def play(_, message: Message): arg = message.text.split(None, 1) if len(arg) < 2: return await message.reply("Use: /play <YouTube link or song name>") target = arg[1] # If name, choose first from mood or do search fallback url = target if target.startswith("http") else MOOD_SONGS.get(target.lower(), [None])[0] if not url: return await message.reply("Song nahi mila. Try with a link or valid mood/name.") path, title = download_audio(url) chat_id = message.chat.id try: await pytgcalls.join_group_call(chat_id, InputStream(InputAudioStream(path))) await message.reply(f"▶️ Now playing: {title}") except Exception: await message.reply("Please start a voice chat first.")

@app.on_message(filters.command("end") & filters.group) async def end_call(_, message: Message): await pytgcalls.leave_group_call(message.chat.id) await message.reply("Left VC and cleared queue.")

async def main(): await app.start() await pytgcalls.start() print("Bot started") await idle() await app.stop()

if name == 'main': import asyncio; asyncio.run(main())

