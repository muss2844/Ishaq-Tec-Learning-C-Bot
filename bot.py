import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# ===========================
# إعدادات البوت
# ===========================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    print("⚠️ BOT_TOKEN is not set! Check Render environment variables.")

ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
DEFAULT_LANGUAGE = "ar"

# ===========================
# تهيئة البوت
# ===========================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ===========================
# نصوص اللغات
# ===========================
MESSAGES = {
    "ar": {
        "welcome": "مرحبًا بك في بوت تعلم لغة C 🖥️\nاختر لغة العرض:",
        "choose_language": "اختر لغتك / Choisissez votre langue:",
        "menu": "القائمة الرئيسية:",
        "lessons": "الدروس",
        "quiz": "الاختبارات",
        "private": "الدروس الخاصة",
    },
    "fr": {
        "welcome": "Bienvenue sur le bot d'apprentissage du langage C 🖥️\nChoisissez votre langue:",
        "choose_language": "اختر لغتك / Choisissez votre langue:",
        "menu": "Menu principal:",
        "lessons": "Leçons",
        "quiz": "Quiz",
        "private": "Leçons privées",
    }
}

# ===========================
# اختيار اللغة
# ===========================
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"))
    keyboard.add(types.InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"))
    await message.answer(MESSAGES["ar"]["choose_language"], reply_markup=keyboard)

# ===========================
# التعامل مع اختيار اللغة
# ===========================
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('lang_'))
async def process_language(callback_query: types.CallbackQuery):
    lang = callback_query.data.split("_")[1]
    text = MESSAGES[lang]["menu"]

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(MESSAGES[lang]["lessons"], callback_data="lessons"))
    keyboard.add(types.InlineKeyboardButton(MESSAGES[lang]["quiz"], callback_data="quiz"))
    keyboard.add(types.InlineKeyboardButton(MESSAGES[lang]["private"], callback_data="private"))

    await bot.send_message(callback_query.from_user.id, text, reply_markup=keyboard)
    await bot.answer_callback_query(callback_query.id)

# ===========================
# تشغيل البوت
# ===========================
if __name__ == "__main__":
    print("Bot is running...")
    executor.start_polling(dp, skip_updates=True)

