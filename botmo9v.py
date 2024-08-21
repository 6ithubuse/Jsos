import os
import random
import json
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Install required libraries
try:
    import telegram
    import requests
except ImportError:
    os.system("pip install python-telegram-bot requests")
    import telegram
    import requests

# TMDB API key
TMDB_API_KEY = "5e4e0e3fa710544994c9280175e0ead7"

# Telegram bot token
TOKEN = "7223092902:AAFUQ6sgLT2sX4UEMf6vRctZ0-uAEnD0MUU"

# Developer ID
DEV_ID = "6994942445"

def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("اقتراحات أفلام", callback_data="movies"),
                InlineKeyboardButton("اقتراحات مسلسلات", callback_data="series")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="مرحباً! ماذا تريد أن تشاهد اليوم؟", reply_markup=reply_markup)

def get_random_suggestion(category):
    url = f"https://api.themoviedb.org/3/{category}/popular?api_key={TMDB_API_KEY}&language=ar&page={random.randint(1, 500)}"
    response = requests.get(url)
    data = response.json()
    random_item = random.choice(data["results"])
    return {
        "name": random_item["title"] if category == "movie" else random_item["name"],
        "image": f"https://image.tmdb.org/t/p/w500{random_item['poster_path']}",
        "rating": f"{random_item['vote_average']}/10",
        "category": ", ".join([genre["name"] for genre in random_item["genre_ids"]])
    }

def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data == "back":
        keyboard = [[InlineKeyboardButton("اقتراحات أفلام", callback_data="movies"),
                    InlineKeyboardButton("اقتراحات مسلسلات", callback_data="series")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=query.message.chat_id, text="اختر نوع الاقتراح:", reply_markup=reply_markup)
    else:
        suggestion = get_random_suggestion(query.data)
        caption = f"🎬 <b>{suggestion['name']}</b>\n\n📊 التقييم: {suggestion['rating']}\n🏷 التصنيف: {suggestion['category']}"
        context.bot.send_photo(chat_id=query.message.chat_id, photo=suggestion['image'], caption=caption, parse_mode="HTML")
        
        keyboard = [[InlineKeyboardButton("اقتراح آخر", callback_data=query.data),
                    InlineKeyboardButton("العودة", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=query.message.chat_id, text="هل تريد اقتراحاً آخر أو العودة للقائمة الرئيسية؟", reply_markup=reply_markup)

def handle_dev_command(update: Update, context: CallbackContext):
    if update.effective_chat.id == DEV_ID:
        command = context.args
        if command[0] == "help":
            help_text = "أوامر المطور:\n"
            help_text += "/dev add [نوع] [اسم] [صورة] [تقييم] [تصنيف] - لإضافة اقتراح جديد\n"
            help_text += "/dev remove [نوع] [اسم] - لحذف اقتراح\n"
            help_text += "/dev list - لعرض قائمة الاقتراحات\n"
            help_text += "/dev update [كود] - لتحديث كود البوت\n"
            context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)
        # Implement other dev commands as needed
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="عذرًا، هذه الميزة متاحة للمطور فقط.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(handle_callback))
    dp.add_handler(CommandHandler("dev", handle_dev_command, pass_args=True))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    