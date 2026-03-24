import discord
import os
import random
import gspread
import logging
from discord.ext import tasks, commands
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
from google.oauth2 import service_account

# Configure logging for better Render visibility
logging.basicConfig(level=logging.INFO)

# read/write access to sheets and google drive
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def get_gspread_client():
    creds = service_account.Credentials.from_service_account_file("creds.json", scopes=SCOPES)
    return gspread.authorize(creds)

def get_used_questions():
    client = get_gspread_client()
    sheet = client.open("Bot Memory").sheet1
    return sheet.col_values(1)  # list of questions in column A

def save_used_question(question):
    client = get_gspread_client()
    sheet = client.open("Bot Memory").sheet1
    sheet.append_row([question])

def clear_used_questions():
    client = get_gspread_client()
    sheet = client.open("Bot Memory").sheet1
    sheet.clear()
    sheet.append_row(["used_questions"]) # Re-add header

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1474277921093849130 

app = Flask('')
@app.route('/')
def home(): return "I'm alive!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- INTENTS FIX ---
intents = discord.Intents.default()
intents.message_content = True  # Required for modern bots to avoid 429/reconnect loops

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Starts the loop before the bot fully logs in
        if not question_of_the_day.is_running():
            question_of_the_day.start()
            print("--- QOTD Task Loop Started ---")

bot = MyBot()

@tasks.loop(hours=24)
async def question_of_the_day():
    await bot.wait_until_ready() 
    print("--- Running Scheduled QOTD Check ---")
    
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"Error: Could not find channel {CHANNEL_ID}. Check permissions.")
        return
    
    # 1. Load Local Questions
    try:
        with open("questions.txt", "r", encoding="utf-8") as f:
            all_questions = [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"Error reading questions.txt: {e}")
        return
    
    # 2. Get Used Questions from Google
    try:
        used_questions = get_used_questions()
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        return
    
    # 3. Filter and Log Count
    available_questions = [q for q in all_questions if q not in used_questions]
    
    # LOG: x out of y questions left
    print(f"STATUS: {len(available_questions)} available out of {len(all_questions)} total questions.")
    
    if not available_questions:
        print("Cycle complete. Clearing sheet and restarting cycle...")
        try:
            clear_used_questions()
            available_questions = all_questions
        except Exception as e:
            print(f"Failed to clear sheet: {e}")
            return

    # 4. Pick and Send
    selected_q = random.choice(available_questions)
    formatted_q = selected_q.replace("{@user}", "@everyone")
    
    try:
        await channel.send(f"**Question of the Day:**\n{formatted_q}")
        save_used_question(selected_q)
        print(f"SUCCESS: Question posted and saved to Sheet.")
    except Exception as e:
        print(f"Failed to send message or save result: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print("------")

# Start Flask then Discord
keep_alive()
try:
    bot.run(TOKEN)
except discord.errors.HTTPException as e:
    if e.status == 429:
        print("CRITICAL: Being rate limited by Cloudflare. Killing process to prevent ban.")
        os._exit(1) # Force stop so Render doesn't loop-restart into a ban
    else:
        raise e
