# 🎧 Telegram Musiqa Qidiruvchi va Yuklovchi Bot

Musiqa qidirish, YouTube havolalari orqali audiolarni eng yuqori sifatda yuklab olish va Telegram orqali tinglovchilarga taqdim etuvchi professional Telegram bot.

---

## ✨ Imkoniyatlari

- 🔍 **Tezkor qidiruv:** Qo'shiq nomi yoki xonanda ismi yozilganda, eng mos natijalar ro'yxatini va interaktiv tugmalarni chiqaradi.
- ⬇️ **1-bosishda yuklab olish:** Tugmani bosish orqali musiqani darhol yuklab beradi.
- 🔗 **YouTube linklar:** Istalgan YouTube yoki YouTube Music havolasini yuborilganda, avtomatik ravishda audiosini ajratib oladi.
- ⚡ **Tezkor Kesh tizimi (SQLite):** Bir marta yuklangan qo'shiqlar bazada saqlanadi va keyingi safar 0.1 soniyada qayta yuboriladi (trafik va vaqt tejaladi).
- 🖼 **Audio metadatalari va muqova (Cover Art):** Qo'shiq nomi, ijrochi va albom rasmi bilan birga audio sifatida yuboradi.
- 💬 **Inline rejim:** Boshqa guruh yoki shaxsiy yozishmalarda ham `@bot_nomi qo'shiq_nomi` deb qidirish imkoniyati.
- 🧵 **Ko'p oqimli (Multi-threading):** Bir vaqtning o'zida bir nechta foydalanuvchi yuklab olganda bot qotib qolmaydi.

---

## 🚀 Ishga tushirish bo'yicha qo'llanma

### 1. Telegramdan Bot Token olish
1. Telegramda [@BotFather](https://t.me/BotFather) botiga kiring.
2. `/newbot` buyrug'ini yuboring.
3. Botingizga nom va username bering (masalan: `MeningMusiqaBot` va `MeningMusiqa_bot`).
4. `@BotFather` sizga **HTTP API token** beradi (masalan: `7123456789:AAH...`).

*(Ixtiyoriy)* **Inline rejimni yoqish:**
- `@BotFather`ga `/setinline` buyrug'ini yuboring.
- Botingizni tanlang va qidiruv so'zini kiriting (masalan: `Musiqa qidirish...`).

---

### 2. Bot tokenini sozlash
Loyihaning asosiy papkasidagi [`.env`](file:///c:/Users/HP%20PC/OYIN/nimadir/.env) faylini oching va tokenni kiriting:

```env
BOT_TOKEN=7123456789:AAHxxxxxxxxxxxxxxxxxxxx
ADMINS=
```

---

### 3. Botni ishga tushirish

Quyidagi buyruq orqali yoki [`start_bot.bat`](file:///c:/Users/HP%20PC/OYIN/nimadir/start_bot.bat) faylini sichqoncha bilan ikki marta bosib ishga tushiring:

```powershell
python bot.py
```

Agar barchasi to'g'ri bajarilgan bo'lsa, konsolda quyidagi xabar chiqadi:
```
Musiqa topuvchi Telegram bot ishga tushmoqda...
Bot muvaffaqiyatli ulandi: @SizningBotNomigiz
Bot xabarlarni kutmoqda. To'xtatish uchun Ctrl+C bosing.
```

---

## 📁 Fayllar tuzilishi

- [`bot.py`](file:///c:/Users/HP%20PC/OYIN/nimadir/bot.py) - Asosiy bot logikasi, buyruqlar, tugmalar va inline rejim.
- [`music_service.py`](file:///c:/Users/HP%20PC/OYIN/nimadir/music_service.py) - YouTube qidiruv va audio yuklab olish xizmati.
- [`database.py`](file:///c:/Users/HP%20PC/OYIN/nimadir/database.py) - SQLite bazasi (foydalanuvchilar va yuklangan audio kesh).
- [`config.py`](file:///c:/Users/HP%20PC/OYIN/nimadir/config.py) - Sozlamalar va `.env` faylini o'qish.
- [`.env`](file:///c:/Users/HP%20PC/OYIN/nimadir/.env) - Bot tokeni va maxfiy ma'lumotlar.
- [`requirements.txt`](file:///c:/Users/HP%20PC/OYIN/nimadir/requirements.txt) - Kerakli kutubxonalar ro'yxati.
- [`start_bot.bat`](file:///c:/Users/HP%20PC/OYIN/nimadir/start_bot.bat) - 1-bosishda Windows orqali botni yurgizish.
