import telebot
import random
import time
import threading
import os

TOKEN = os.getenv("8699033001:AAGhYLpSrpm79HebzovzqFwZSvCrNK-3T3c")
CHAT_ID = "7661174841" 
bot = telebot.TeleBot(TOKEN)

MATCHS_EXPLOSIFS = [
    {
        "match": "🔥 Arsenal 1-1 Chelsea 87'",
        "analyse": "xG: 1.8-2.1 | Tirs 85-90': 4\n⚡ Les 2 équipes poussent.",
        "enjeu": "Course à l'Europe. Chelsea doit gagner.",
        "pari": "Under 2.5 @1.52 | BTTS Oui @1.80"
    },
    {
        "match": "🔥 Real 2-1 Barca 82'", 
        "analyse": "xG: 2.4-1.9 | Rouge Barca 80'\n⚡ Real peut tuer à 11v10.",
        "enjeu": "Clasico. Barca ultra dangereux en contre.",
        "pari": "Real @1.90 | Over 3.5 @2.05"
    }
]

def scanner_24h24():
    while True:
        if random.randint(1, 8) == 1:
            data = random.choice(MATCHS_EXPLOSIFS)
            msg = f"🚨 ALERTE MATCH EXPLOSIF 70'+ 🚨\n\n{data['match']}\n\n📊 {data['analyse']}\n🎯 {data['enjeu']}\n💰 {data['pari']}"
            bot.send_message(CHAT_ID, msg)
        time.sleep(30)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot 70'+ EXPLOSIF 24/24 ✅\nHébergé sur Railway\n/explosif")

@bot.message_handler(commands=['explosif'])
def match_explosif(message):
    data = random.choice(MATCHS_EXPLOSIFS)
    msg = f"🚨 MATCH EXPLOSIF 70'+ 🚨\n\n{data['match']}\n\n📊 {data['analyse']}\n🎯 {data['enjeu']}\n💰 {data['pari']}"
    bot.send_message(message.chat.id, msg)

print("Bot Railway 24/24 lancé...")
threading.Thread(target=scanner_24h24, daemon=True).start()
bot.infinity_polling()
