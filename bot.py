import os
import sys

# Windows konsolida Unicode/emojilar to'g'ri chiqishi uchun:
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import threading
import telebot
from telebot import types
import config
import database
import music_service

if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE" or ":" not in config.BOT_TOKEN:
    print("=" * 65)
    print("! DIQQAT: Bot tokeni kiritilmagan yoki noto'g'ri!")
    print("1. Telegramda @BotFather ga kiring va yangi bot yarating (/newbot).")
    print("2. Olingan tokenni '.env' faylidagi BOT_TOKEN ga qo'ying.")
    print("   Masalan: BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRstuVWxyz")
    print("3. So'ngra 'python bot.py' buyrug'i orqali botni ishga tushiring.")
    print("=" * 65)
    sys.exit(1)


bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode="HTML")


# Ma'lumotlar bazasini ishga tushirish
database.init_db()

@bot.message_handler(commands=['start'])
def handle_start(message: types.Message):
    user = message.from_user
    database.register_user(user.id, user.username, user.first_name)
    
    welcome_text = (
        f"🎧 <b>Assalomu alaykum, {user.first_name}!</b>\n\n"
        "Men musiqa qidiruvchi va eng yaxshi sifatda yuklab beruvchi botman! 🎵\n\n"
        "<b>Qanday foydalanish mumkin?</b>\n"
        "1. Menga qo'shiq yoki ijrochi nomini yozib yuboring (masalan: <code>Xamdam Sobirov</code> yoki <code>Believer</code>)\n"
        "2. Yoki to'g'ridan-to'g'ri <b>YouTube</b> havolasini yuboring\n\n"
        "🔍 Hoziroq istalgan qo'shiq nomini yozing!"
    )
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔥 Ommabop qo'shiqlar", "ℹ️ Yordam")
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda msg: msg.text == "ℹ️ Yordam")
def handle_help(message: types.Message):
    help_text = (
        "📌 <b>Botdan foydalanish yo'riqnomasi:</b>\n\n"
        "• <b>Musiqa qidirish:</b> Shunchaki qo'shiq nomini yoki xonandani yozing. Bot sizga eng mos natijalarni chiqaradi.\n"
        "• <b>Tugmani bosing:</b> Ro'yxatdan o'zingizga yoqqan raqamdagi tugmani bossangiz, musiqa tezda yuklab beriladi.\n"
        "• <b>YouTube havolasi:</b> YouTube'dagi videoning linkini yuborsangiz, uning audio formatini olib beradi.\n"
        "• <b>Tezkor kesh:</b> Oldin yuklangan qo'shiqlar bir soniyada jo'natiladi!\n\n"
        "Savol yoki takliflar bo'lsa: @BotFather orqali bog'lanishingiz mumkin."
    )
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['stats'])
def handle_stats(message: types.Message):
    stats = database.get_stats()
    text = (
        "📊 <b>Bot Statistikasi:</b>\n\n"
        f"👤 Foydalanuvchilar: <b>{stats['users']}</b> ta\n"
        f"🎵 Keshdagi qo'shiqlar: <b>{stats['tracks']}</b> ta\n"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda msg: msg.text == "🔥 Ommabop qo'shiqlar")
def handle_trending(message: types.Message):
    send_search_results(message.chat.id, "Top Uzbek Music 2026", "🔥 Ommabop musiqalar")

def send_search_results(chat_id: int, query: str, header_text: str = None):
    wait_msg = bot.send_message(chat_id, "🔍 <i>Qidirilmoqda, iltimos kuting...</i>")
    
    try:
        results = music_service.search_music(query, limit=7)
        
        if not results:
            bot.edit_message_text(
                "😔 Kechirasiz, ushbu nom bo'yicha musiqa topilmadi.\nIltimos, nomini boshqacharoq yozib ko'ring.",
                chat_id=chat_id,
                message_id=wait_msg.message_id
            )
            return

        title_header = header_text if header_text else f"🔍 <b>\"{query}\"</b> bo'yicha topilgan natijalar:"
        text_lines = [title_header, ""]
        
        keyboard = types.InlineKeyboardMarkup()
        
        for idx, item in enumerate(results, start=1):
            title = item['clean_title']
            if len(title) > 42:
                title = title[:39] + "..."
            duration_str = item['duration_str']
            text_lines.append(f"<b>{idx}.</b> {title} <code>({duration_str})</code>")
            
            # Tugma matni
            btn_title = f"{idx}. {title} ({duration_str})"
            callback_data = f"dl:{item['id']}"
            keyboard.add(types.InlineKeyboardButton(text=btn_title, callback_data=callback_data))

        text_lines.append("\n👇 <i>Musiqani yuklab olish uchun yuqoridagi tugmalardan birini bosing:</i>")
        final_text = "\n".join(text_lines)
        
        bot.edit_message_text(
            text=final_text,
            chat_id=chat_id,
            message_id=wait_msg.message_id,
            reply_markup=keyboard
        )
    except Exception as e:
        bot.edit_message_text(f"⚠️ Xatolik yuz berdi: {str(e)}", chat_id=chat_id, message_id=wait_msg.message_id)

def download_and_send_worker(chat_id: int, video_id: str, status_msg_id: int = None):
    try:
        # 1. Keshni tekshirish
        cached = database.get_cached_track(video_id)
        bot_info = bot.get_me()
        bot_tag = f"@{bot_info.username}" if bot_info and bot_info.username else "@MusiqaBot"
        
        if cached:
            caption = f"🎵 <b>{cached['title']}</b>\n👤 {cached['performer']}\n\n🤖 {bot_tag}"
            bot.send_audio(
                chat_id=chat_id,
                audio=cached['file_id'],
                caption=caption,
                title=cached['title'],
                performer=cached['performer'],
                duration=cached['duration']
            )
            if status_msg_id:
                try:
                    bot.delete_message(chat_id, status_msg_id)
                except Exception:
                    pass
            return

        # 2. Yangidan yuklab olish
        dl_res = music_service.download_audio_by_id(video_id)
        if not dl_res['success']:
            err_msg = dl_res.get('error', 'Noma\'lum xatolik')
            if "max_filesize" in err_msg.lower():
                err_text = "⚠️ Bu musiqa fayli hajmi juda katta (50MB dan ortiq), uni yuklab bo'lmaydi."
            else:
                err_text = f"⚠️ Yuklab olishda xatolik yuz berdi: {err_msg}"
                
            if status_msg_id:
                bot.edit_message_text(err_text, chat_id=chat_id, message_id=status_msg_id)
            else:
                bot.send_message(chat_id, err_text)
            return

        file_path = dl_res['file_path']
        thumb_path = dl_res.get('thumbnail_path')
        title = dl_res.get('title', 'Musiqa')
        performer = dl_res.get('performer', 'Noma\'lum ijrochi')
        duration = dl_res.get('duration', 0)

        # Telegramga audio jo'natish
        with open(file_path, 'rb') as audio_file:
            thumb_file = open(thumb_path, 'rb') if (thumb_path and os.path.exists(thumb_path)) else None
            caption = f"🎵 <b>{title}</b>\n👤 {performer}\n\n🤖 {bot_tag}"
            
            sent_msg = bot.send_audio(
                chat_id=chat_id,
                audio=audio_file,
                caption=caption,
                title=title,
                performer=performer,
                duration=duration,
                thumb=thumb_file
            )
            
            if thumb_file:
                thumb_file.close()

        # Telegram file_id sini keshga yozish
        if sent_msg and sent_msg.audio:
            database.save_cached_track(
                video_id=video_id,
                file_id=sent_msg.audio.file_id,
                title=title,
                performer=performer,
                duration=duration
            )

        # Holat xabarini o'chirish
        if status_msg_id:
            try:
                bot.delete_message(chat_id, status_msg_id)
            except Exception:
                pass

        # Vaqtinchalik fayllarni tozalash
        music_service.cleanup_files(file_path, thumb_path)

    except Exception as e:
        print(f"Xatolik (download_and_send_worker): {e}")
        if status_msg_id:
            try:
                bot.edit_message_text(f"⚠️ Xatolik yuz berdi: {str(e)}", chat_id=chat_id, message_id=status_msg_id)
            except Exception:
                pass

@bot.callback_query_handler(func=lambda call: call.data.startswith("dl:"))
def handle_download_callback(call: types.CallbackQuery):
    video_id = call.data.split(":", 1)[1]
    
    bot.answer_callback_query(call.id, text="⚡ Musiqa tayyorlanmoqda...")
    status_msg = bot.send_message(call.message.chat.id, "⏳ <i>Musiqa yuklab olinmoqda, iltimos biroz kuting...</i>")
    
    # Yuklab olishni alohida oqimda (Thread) ishga tushirish (bot qotib qolmasligi uchun)
    thread = threading.Thread(
        target=download_and_send_worker,
        args=(call.message.chat.id, video_id, status_msg.message_id)
    )
    thread.daemon = True
    thread.start()

# YouTube havolasi yoki matnli qidiruv
@bot.message_handler(content_types=['text'])
def handle_text_message(message: types.Message):
    text = message.text.strip()
    user = message.from_user
    database.register_user(user.id, user.username, user.first_name)
    
    if text.startswith("/"):
        return

    # Agar YouTube havolasi yuborilgan bo'lsa
    if "youtube.com/watch" in text or "youtu.be/" in text:
        video_id = None
        if "youtu.be/" in text:
            video_id = text.split("youtu.be/")[1].split("?")[0].split("&")[0]
        elif "v=" in text:
            video_id = text.split("v=")[1].split("&")[0]
            
        if video_id:
            status_msg = bot.send_message(message.chat.id, "⏳ <i>Havola orqali audio yuklab olinmoqda...</i>")
            thread = threading.Thread(
                target=download_and_send_worker,
                args=(message.chat.id, video_id, status_msg.message_id)
            )
            thread.daemon = True
            thread.start()
            return

    # Oddiy matnli qidiruv
    send_search_results(message.chat.id, text)

# Inline rejim (@botname orqali boshqa chatlarda musiqa qidirish)
@bot.inline_handler(lambda query: len(query.query) > 1)
def handle_inline_query(query: types.InlineQuery):
    try:
        user_query = query.query.strip()
        results = music_service.search_music(user_query, limit=8)
        
        inline_results = []
        for item in results:
            title = item['clean_title']
            performer = item['performer']
            v_id = item['id']
            
            # Agar keshda mavjud bo'lsa, to'g'ridan-to'g'ri audio jo'natadi
            cached = database.get_cached_track(v_id)
            if cached:
                r = types.InlineQueryResultCachedAudio(
                    id=v_id,
                    audio_file_id=cached['file_id'],
                    caption=f"🎵 {title}\n👤 {performer}"
                )
            else:
                # Keshda bo'lmasa xabar va yuklab olish tugmasi
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text="⬇️ Musiqani yuklab olish", callback_data=f"dl:{v_id}"))
                r = types.InlineQueryResultArticle(
                    id=v_id,
                    title=title,
                    description=f"{performer} ({item['duration_str']})",
                    input_message_content=types.InputTextMessageContent(
                        f"🎵 <b>{title}</b>\n👤 {performer}\n⏱ Davomiyligi: {item['duration_str']}\n\nQuyidagi tugma orqali yuklab oling:",
                        parse_mode="HTML"
                    ),
                    reply_markup=markup
                )
            inline_results.append(r)
            
        bot.answer_inline_query(query.id, inline_results, cache_time=60)
    except Exception as e:
        print(f"Inline xatolik: {e}")

if __name__ == "__main__":
    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("Xatolik: Bot tokenini .env fayliga kiriting!")
        sys.exit(1)
        
    print("Musiqa topuvchi Telegram bot ishga tushmoqda...")
    try:
        me = bot.get_me()
        print(f"Bot muvaffaqiyatli ulandi: @{me.username} ({me.first_name})")
    except Exception as e:
        print(f"Botga ulanishda xatolik: {e}")
        print("Iltimos, .env faylidagi BOT_TOKEN to'g'ri ekanligini tekshiring.")
        sys.exit(1)
        
    print("Bot xabarlarni kutmoqda. To'xtatish uchun Ctrl+C bosing.")
    bot.infinity_polling(skip_pending=True)
