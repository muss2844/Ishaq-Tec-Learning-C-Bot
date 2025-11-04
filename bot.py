import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from database import init_db, add_order, update_status
from config import BOT_TOKEN, ADMIN_ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ==============================
# البدء
# ==============================
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📱 تعبئة الرصيد")
    await msg.answer("👋 أهلاً بك في خدمة تعبئة الرصيد.\nاضغط على الزر أدناه للبدء:", reply_markup=kb)

# ==============================
# اختيار الشبكة
# ==============================
@dp.message_handler(lambda m: m.text == "📱 تعبئة الرصيد")
async def choose_operator(msg: types.Message):
    kb = types.InlineKeyboardMarkup()
    for op in ["موبيليس", "جيزي", "أوريدو"]:
        kb.add(types.InlineKeyboardButton(op, callback_data=f"op_{op}"))
    await msg.answer("📶 اختر الشبكة:", reply_markup=kb)

# ==============================
# اختيار المبلغ
# ==============================
@dp.callback_query_handler(lambda c: c.data.startswith("op_"))
async def choose_amount(call: types.CallbackQuery):
    op = call.data.split("_")[1]
    kb = types.InlineKeyboardMarkup()
    for amount in [100, 200, 500, 1000, 2000]:
        kb.add(types.InlineKeyboardButton(f"{amount} دج", callback_data=f"amount_{op}_{amount}"))
    await call.message.edit_text(f"💰 اختر المبلغ لشركة {op}:", reply_markup=kb)

# ==============================
# إدخال رقم الهاتف
# ==============================
user_temp = {}

@dp.callback_query_handler(lambda c: c.data.startswith("amount_"))
async def ask_phone(call: types.CallbackQuery):
    _, op, amount = call.data.split("_")
    user_temp[call.from_user.id] = {"operator": op, "amount": amount}
    await call.message.edit_text(f"📞 أرسل رقم الهاتف لتعبئة {amount} دج ({op}):")

# ==============================
# تأكيد الطلب
# ==============================
@dp.message_handler(lambda m: m.text.isdigit() and len(m.text) >= 8)
async def confirm_order(msg: types.Message):
    if msg.from_user.id not in user_temp:
        return await msg.answer("⚠️ ابدأ من /start من فضلك.")

    info = user_temp[msg.from_user.id]
    op, amount = info["operator"], info["amount"]
    phone = msg.text

    add_order(msg.from_user.id, msg.from_user.username, phone, op, amount)
    await msg.answer(f"✅ تم إرسال طلب تعبئة {amount} دج لشركة {op}.\n📞 رقم: {phone}\n"
                     f"⏳ انتظر التأكيد من البائع.")

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ تمت التعبئة", callback_data=f"done_{phone}"),
        types.InlineKeyboardButton("❌ رفض", callback_data=f"cancel_{phone}")
    )

    await bot.send_message(ADMIN_ID, f"📢 طلب جديد:\n"
                                     f"👤 المستخدم: @{msg.from_user.username or msg.from_user.full_name}\n"
                                     f"📞 رقم الهاتف: {phone}\n"
                                     f"🏷️ الشركة: {op}\n"
                                     f"💰 المبلغ: {amount} دج", reply_markup=kb)
    del user_temp[msg.from_user.id]

# ==============================
# أزرار المدير
# ==============================
@dp.callback_query_handler(lambda c: c.data.startswith("done_") or c.data.startswith("cancel_"))
async def handle_admin_action(call: types.CallbackQuery):
    phone = call.data.split("_")[1]
    status = "تمت" if call.data.startswith("done_") else "مرفوضة"
    update_status(phone, status)

    await call.message.edit_text(f"✅ تم تحديث حالة الطلب ({status}) لرقم {phone}")
    await call.answer("👌 تم التنفيذ")

if __name__ == "__main__":
    init_db()
    print("📲 Bot is running...")
    executor.start_polling(dp, skip_updates=True)
