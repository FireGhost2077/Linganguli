from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Tokenul botului (nu expune public tokenul în codul real)
TOKEN = '8065308480:AAHEb8pv_hjej-SWncGg90VAITr5zFN-3IE'

# Dicționar pentru stările utilizatorilor
user_statuses = {}
# Listă pentru păstrarea ID-urilor mesajelor trimise de bot
bot_messages = []

# Funcția pentru comanda /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_statuses[user_id] = ""  # Inițial, statusul este gol
    await update.message.reply_text(
        "Salut! Acest bot îți permite să-ți setezi statusul. Alege un status folosind butoanele."
    )
    await send_status_buttons(update, context)

# Funcția pentru trimiterea butoanelor pentru alegerea statusului
async def send_status_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Dorm blya", callback_data="status_afk")],
        [InlineKeyboardButton("Ocupat pizdeț", callback_data="status_busy")],
        [InlineKeyboardButton("Disponibil", callback_data="status_available")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        sent_message = await update.message.reply_text("Alegeți un status:", reply_markup=reply_markup)
        # Adăugăm ID-ul mesajului trimis de bot în listă
        bot_messages.append(sent_message.message_id)

# Funcția pentru gestionarea alegerea statusului
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if query.data == "status_afk":
        user_statuses[user_id] = "Dorm blya"
    elif query.data == "status_busy":
        user_statuses[user_id] = "Ocupat pizdeț"
    elif query.data == "status_available":
        user_statuses[user_id] = "Disponibil"

    # Actualizarea mesajului cu noul status și trimiterea din nou a butoanelor
    await query.edit_message_text(f"Statusul tău a fost actualizat: {user_statuses[user_id]}")
    await send_status_buttons(update, context)

    # Verificăm dacă toți utilizatorii și-au ales statusul
    if all(status != "" for status in user_statuses.values()):
        # Apelăm funcția de ștergere a mesajelor botului
        if query.message:
            await delete_bot_messages(context, query.message.chat.id)

# Funcția pentru ștergerea mesajelor trimise de bot
async def delete_bot_messages(context, chat_id):
    for message_id in bot_messages:
        try:
            await context.bot.delete_message(chat_id, message_id)
        except Exception as e:
            print(f"Eroare la ștergerea mesajului {message_id}: {e}")
    # Resetăm lista după ce am șters toate mesajele
    bot_messages.clear()

# Funcția pentru răspunsul la mesaje în chat
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_statuses and user_statuses[user_id]:
        # Verificăm dacă este un mesaj într-un chat de grup sau într-un mesaj direct
        if isinstance(update.message, Message) and update.message.chat.type in ['group', 'supergroup']:
            # Verificăm dacă utilizatorul este disponibil pentru a afișa statusurile
            if user_statuses[user_id] != "Disponibil":
                # Trimiterea mesajului cu statusul utilizatorilor din grup
                status_messages = []
                for member_id, status in user_statuses.items():
                    if status:  # Verificăm dacă există un status pentru acel utilizator
                        member = await update.message.chat.get_member(member_id)
                        member_name = member.user.first_name if member.user.first_name else "Utilizator"
                        status_messages.append(f"{member_name}: {status}")

                if status_messages:
                    await update.message.reply_text("\n".join(status_messages))

# Funcția pentru comanda /stat
async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_messages = []
    for member_id, status in user_statuses.items():
        if status:  # Verificăm dacă există un status pentru acel utilizator
            member = await update.message.chat.get_member(member_id)
            member_name = member.user.first_name if member.user.first_name else "Utilizator"
            status_messages.append(f"{member_name}: {status}")

    if status_messages:
        await update.message.reply_text("\n".join(status_messages))

# Lansarea aplicației botului
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CommandHandler("stat", stat))

    print("Botul a fost lansat")
    app.run_polling()
