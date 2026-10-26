import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Admin Telegram IDlari (vergul bilan ajratilgan, masalan: 12345678,87654321)
ADMINS_RAW = os.getenv("ADMINS", "")
ADMIN_IDS = [int(i.strip()) for i in ADMINS_RAW.split(",") if i.strip().isdigit()]
