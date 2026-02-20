import discord
import os
import random
import gspread
from discord.ext import tasks, commands
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
from google.oauth2 import service_account

# read/write access to sheets and google drive - needs API to be enabled in google cloud
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
    sheet.append_row(["used_questions"]) # need to re-add header

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1474277921093849130 

app = Flask('')
@app.route('/')
def home(): return "I'm alive!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@tasks.loop(hours=24)
async def question_of_the_day():
    await bot.wait_until_ready() 
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Error: Could not find channel. Check your CHANNEL_ID.")
        return
    
    try:
        with open("questions.txt", "r", encoding="utf-8") as f:
            all_questions = [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"Error reading questions.txt: {e}")
        return
    
    try:
        used_questions = get_used_questions()
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        return
    
    available_questions = [q for q in all_questions if q not in used_questions]
    
    if not available_questions:
        print("Cycle complete. Clearing sheet and restarting...")
        clear_used_questions()
        available_questions = all_questions

    selected_q = random.choice(available_questions)
    formatted_q = selected_q.replace("{@user}", "@everyone")
    
    try:
        await channel.send(f"**Question of the Day:**\n{formatted_q}")
        save_used_question(selected_q)
    except Exception as e:
        print(f"Failed to send message: {e}")

@bot.event
async def on_ready():
    keep_alive()
    print(f'Logged in as {bot.user}')
    if not question_of_the_day.is_running():
        question_of_the_day.start()

bot.run(TOKEN)