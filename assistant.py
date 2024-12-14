from tinydb import TinyDB, Query
from telegram import Update
from telegram.ext import Application, CommandHandler,  ContextTypes, filters
import os
import logging
import requests
import json
from dotenv import load_dotenv

logging.basicConfig(level=logging.WARNING, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                    filename="bot.log",
                    filemode="a")
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

db_users_file = "./users.json"
if not os.path.exists(db_users_file):
    with open(db_users_file, "w") as file:
        file.write("{}")
db = TinyDB(db_users_file)
User = Query()


async def get_horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://deployhoroscope.ru/api/v1/day"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # Process the response
        good_signs = []
        bad_signs = []
        neutral_signs = []
        
        # Group signs by status
        for sign in data['result']['signs']:
            if sign['status'] == 'good':
                good_signs.append(sign['name_ru'])
                good_comment = sign['comment']
            elif sign['status'] == 'bad':
                bad_signs.append(sign['name_ru'])
                bad_comment = sign['comment']
            else:
                neutral_signs.append(sign['name_ru'])
                neutral_comment = sign['comment']
        
        # Prepare the message
        message = f"Гороскоп деплоя на {data['result']['day']} {data['result']['month']['name_ru']} {data['result']['year']}\n\n"
        
        if good_signs:
            message += "✅ БЛАГОПРИЯТНО:\n"
            message += f"{', '.join(good_signs)}\n"
            message += f"{good_comment}\n\n"
            
        if neutral_signs:
            message += "⚠️ НЕЙТРАЛЬНО:\n"
            message += f"{', '.join(neutral_signs)}\n"
            message += f"{neutral_comment}\n\n"
            
        if bad_signs:
            message += "❌ НЕБЛАГОПРИЯТНО:\n"
            message += f"{', '.join(bad_signs)}\n"
            message += f"{bad_comment}"
        
        await update.message.reply_text(message)
        
    except Exception as e:
        await update.message.reply_text("Произошла ошибка при получении гороскопа.")
        print(f"Error: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("horoscope", get_horoscope))

    print("Bot started...")
    app.run_polling()

if __name__ == '__main__':
    main()