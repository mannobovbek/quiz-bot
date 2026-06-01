from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@Registan_LC"
API_BASE = os.getenv("API_BASE", "http://backend:8000")

