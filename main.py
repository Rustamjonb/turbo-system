import random
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

BOT_TOKEN = '8231786450:AAFa-9wPFPlVkMXocPLbBska69-PnvKuID0'
ADMIN_ID = 7074284845
CHANNEL_ID = -1002771722016

user_data = {}
TOUR_PACKS = [
    "🏔️ Qoraqo'y- Bir kunlik ekskursiya : 380,000 so'm",
    "🏜️ Arslonbob-ikki kunlik unutilmas sayohat:  599,000",
    "🏞️ Sayr-Chelek-tabiat qo'ynidagi unutilmas sayohat: 699,000"
]

async def send_main_menu(chat_id, bot):
    buttons = [
        [InlineKeyboardButton("🎒 Tur paketlar", callback_data="tourpacks")],
        [InlineKeyboardButton("🛂 Viza yordami", callback_data="visa")],
        [InlineKeyboardButton("🚆✈️ Chipta bron qilish", callback_data="ticket")],
        [InlineKeyboardButton("📞 Admin bilan bog‘lanish", url="https://t.me/rustamrazzokov")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await bot.send_message(chat_id=chat_id, text="Xizmat turini tanlang:", reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_data[user_id] = {}
    await update.message.reply_text("Salom! Ismingizni kiriting:")

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if "name" not in user_data[user_id]:
        user_data[user_id]["name"] = update.message.text
        button = [[KeyboardButton("📱 Kontakt yuborish", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(button, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Endi iltimos, telefon raqamingizni yuboring:", reply_markup=reply_markup)
        return
    if "contact" not in user_data[user_id]:
        await update.message.reply_text("Iltimos, raqamingizni yuboring.")
        return

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    phone = update.message.contact.phone_number
    user_data[user_id]["contact"] = phone
    await send_main_menu(chat_id=user_id, bot=context.bot)

async def handle_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.message.chat_id

    if query.data == "tourpacks":
        selected_tours = random.sample(TOUR_PACKS, 3)
        buttons = [[InlineKeyboardButton(tour, callback_data=tour)] for tour in selected_tours]
        buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back")])
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_text("Quyidagi turlar hozirda mavjud:", reply_markup=reply_markup)

    elif query.data == "visa":
        user_data[user_id]["next_step"] = "visa_info"
        back_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back")]
        ])
        await query.edit_message_text("Viza uchun qanday mamlakat va ma'lumot kerak? Iltimos yozing.", reply_markup=back_markup)

    elif query.data == "ticket":
        user_data[user_id]["next_step"] = "ticket_info"
        back_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back")]
        ])
        await query.edit_message_text("Qaysi yo‘nalishga va qachon chipta kerak?", reply_markup=back_markup)

    elif query.data == "back":
        await send_main_menu(chat_id=user_id, bot=context.bot)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if user_id not in user_data or "name" not in user_data[user_id]:
        await get_name(update, context)
        return

    if "next_step" in user_data[user_id]:
        step = user_data[user_id].pop("next_step")
        name = user_data[user_id].get("name", "Noma'lum")
        phone = user_data[user_id].get("contact", "Yo‘q")
        msg = ""

        if step == "visa_info":
            msg = f"🛂 Viza yordami:\n👤 Ism: {name}\n📞 Raqam: {phone}\n✉️ Ma'lumot: {update.message.text}"
        elif step == "ticket_info":
            msg = f"🚆✈️ Chipta so‘rovi:\n👤 Ism: {name}\n📞 Raqam: {phone}\n✉️ Yo‘nalish/vaqt: {update.message.text}"

        await update.message.reply_text("Ma'lumot uchun rahmat! Tez orada siz bilan bog‘lanamiz.")
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
            await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
        except Exception as e:
            print(f"Xatolik yuborishda: {e}")


    else:
        await get_name(update, context)

async def tour_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.message.chat_id
    selected_tour = query.data
    user_data[user_id]["tour"] = selected_tour

    name = user_data[user_id].get("name", "Noma'lum")
    phone = user_data[user_id].get("contact", "Yo‘q")
    msg = f"""📥 Yangi buyurtma:
👤 Ism: {name}
📞 Raqam: {phone}
🧭 Tanlangan tur: {selected_tour}"""

    await query.edit_message_text("Siz bilan tez orada aloqaga chiqamiz. Batafsil : @oybektravel")
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
    except Exception as e:
        print(f"Xatolik admin/kanalga yuborishda: {e}")

async def forward_everything(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        try:
            await update.message.forward(chat_id=ADMIN_ID)
        except Exception as e:
            print(f"❌ Xatolik forwardda: {e}")

# SETUP
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_option, pattern="^(tourpacks|visa|ticket|back)$"))
app.add_handler(CallbackQueryHandler(tour_selected))
app.add_handler(MessageHandler(filters.CONTACT, get_contact))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.ALL, forward_everything))

print("✅ Bot is running...")
app.run_polling()
