# Curious Llama

A Python-based Discord bot that posts a random "Question of the Day" on a specified channel every 24 hours.

## 🚀 Features
- **Over 300 Questions:** Large rotation of unique prompts.
- **Persistent Memory:** Uses Google Sheets API to ensure questions don't repeat, even if the host restarts.
- **Auto-Ping:** Mentions `@everyone` for maximum engagement, but can be customized to mention individual users at random, or a specific role.
- **Free 24/7 Hosting:** Runs on Render with a Flask keep-alive server via UptimeRobot.
# 📢 QOTD Bot (Question of the Day)

An automated Discord bot built with `discord.py` that posts a unique, engaging question every 24 hours. It uses Google Sheets as a persistent database to ensure questions never repeat, even when hosted on ephemeral platforms like Render.
---

## 🛠️ DIY: Make This Your Own

If you want to use this repository as a base for your own bot, follow these instructions:

### 1. Discord Setup
1. Create an application at the [Discord Developer Portal](https://discord.com/developers/applications).
2. Go to the **Bot** tab and reset/copy your **Token**.
3. Enable **Message Content Intent** under the Privileged Gateway Intents section.
4. Copy the **Channel ID** of the Discord channel where you want the questions to appear.

### 2. Google Sheets API 
Since Render's file system is temporary, this bot uses Google Sheets to remember which questions it has already asked.
1. Create a Google Sheet named `Bot Memory`.
2. Go to [Google Cloud Console](https://console.cloud.google.com/), create a project, and enable the **Google Sheets** and **Google Drive** APIs.
3. Create a **Service Account** under "Credentials," download the **JSON Key**, and rename it to `creds.json`.
4. Open `creds.json`, copy the `client_email`, and **Share** your Google Sheet with that email as an **Editor**.

### 3. Code Adjustments
- Replace the `CHANNEL_ID` in `main.py` with your specific Discord Channel ID.
- Add your own questions to `questions.txt` (one per line). Use `{@user}` as a placeholder if you wish to swap it for mentions.

---

## ☁️ Deployment Instructions (Render)

1. **GitHub:** Upload the code to a **Private** repository. 
   * *Note: Ensure `.env` and `creds.json` are in your `.gitignore` so they are never public.*
2. **Render Web Service:**
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `python main.py`
3. **Environment Variables:** Add `DISCORD_TOKEN` with your bot token.
4. **Secret Files:** Create a secret file named `creds.json` and paste the entire contents of your local JSON key file.
5. **Uptime:** Use [UptimeRobot](https://uptimerobot.com) to ping your Render service URL every 5 minutes to prevent the bot from "spinning down."

---

## 📦 Requirements
- `discord.py`
- `gspread`
- `google-auth`
- `flask`
- `python-dotenv`

---

## ⚖️ License
This project is open-source. Feel free to fork and modify for your own community!
