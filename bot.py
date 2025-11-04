import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import sqlite3

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

def init_db():
    conn = sqlite3.connect("orders.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            phone TEXT,
            operator TEXT,
            amount INTEGER,
            status TEXT DEFAULT 'pending'
        )
    """)
    conn.commit()
    conn.close()

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📱 تعبئة الرصيد")
    await msg.answer("👋 أهلاً بك! اختر خدمة:", reply_markup=kb)

@dp.message_handler(lambda m: m.text == "📱 تعبئة الرصيد")
async def choose_operator(msg: types.Message):
    kb = types.InlineKeyboardMarkup()
    for op in ["موبيليس", "جيزي", "أوريدو"]:
        kb.add(types.InlineKeyboardButton(op, callback_data=f"op_{op}"))
    await msg.answer("اختر الشركة:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("op_"))
async def choose_amount(call: types.CallbackQuery):
    op = call.data.split("_")[1]
    kb = types.InlineKeyboardMarkup()
    for amount in [100, 200, 500, 1000, 2000]:
        kb.add(types.InlineKeyboardButton(f"{amount} دج", callback_data=f"amount_{op}_{amount}"))
    await call.message.edit_text(f"💰 اختر المبلغ ({op}):", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("amount_"))
async def ask_phone(call: types.CallbackQuery):
    _, op, amount = call.data.split("_")
    await call.message.edit_text(f"📞 أرسل رقم الهاتف لشركة {op} لشحن {amount} دج.")
    await bot.send_message(call.from_user.id, f"اكتب رقم الهاتف الآن:")
    dp.current_operator = op
    dp.current_amount = amount

@dp.message_handler(lambda m: m.text.isdigit() and len(m.text) >= 8)
async def confirm_order(msg: types.Message):
    phone = msg.text
    op = getattr(dp, "current_operator", None)
    amount = getattr(dp, "current_amount", None)
    if not op:
        return await msg.answer("⚠️ من فضلك ابدأ من /start")

    conn = sqlite3.connect("orders.db")
    c = conn.cursor()
    c.execute("INSERT INTO orders (user_id, phone, operator, amount) VALUES (?, ?, ?, ?)",
              (msg.from_user.id, phone, op, amount))
    conn.commit()
    conn.close()

    await msg.answer(f"✅ تم إرسال طلب تعبئة {amount} دج لشركة {op}.\n📞 رقم: {phone}")
    await bot.send_message(ADMIN_ID, f"📢 طلب جديد:\n"
                                     f"👤 {msg.from_user.full_name}\n"
                                     f"📞 {phone}\n"
                                     f"🏷️ {op}\n"
                                     f"💰 {amount} دج",
                           reply_markup=types.InlineKeyboardMarkup().add(
                               types.InlineKeyboardButton("✅ تمت التعبئة", callback_data=f"done_{phone}"),
                               types.InlineKeyboardButton("❌ رفض", callback_data=f"cancel_{phone}")
                           ))

@dp.callback_query_handler(lambda c: c.data.startswith("done_") or c.data.startswith("cancel_"))
async def handle_admin_action(call: types.CallbackQuery):
    phone = call.data.split("_")[1]
    status = "done" if call.data.startswith("done_") else "cancelled"

    conn = sqlite3.connect("orders.db")
    c = conn.cursor()
    c.execute("UPDATE orders SET status = ? WHERE phone = ?", (status, phone))
    conn.commit()
    conn.close()

    await call.message.edit_text(f"تم تحديث حالة الطلب ({status}) لرقم {phone}")
    await call.answer("👌")

if __name__ == "__main__":
    init_db()
    executor.start_polling(dp, skip_updates=True)
