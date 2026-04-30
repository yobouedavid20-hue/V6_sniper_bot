import telebot
import random
import time
import threading
import os

CHAT_ID = "7661174841"

MATCHS_EXPLOSIFS = [
    {
        "match": "🔥 Arsenal 1-1 Chelsea 70'",
        "analyse": "xG: 1.8-2.1 | Tirs: 12-9",
        "enjeu": "Course à l'Europe.",
        "pari": "Under 2.5 @1.52 | BTTS Non @1.90"
    },
    {
        "match": "🔥 Real 2-1 Barca 85'",
        "analyse": "xG: 2.4-1.9 | Rouges: 0-1",
        "enjeu": "Clasico. Barca ultra offensif",
        "pari": "Real @1.90 | Over 3.5 @2.10"
    }
]

def envoyer_match():
    match = random.choice(MATCHS_EXPLOSIFS)
    texte = f"{match['match']}\n{match['analyse']}\n{match['enjeu']}\n💣 Pari: {match['pari']}"
    bot.send_message(CHAT_ID, texte)

def boucle_auto():
    while True:
        envoyer_match()
        time.sleep(1800)

def start_polling():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    TOKEN = os.getenv("TOKEN")
    if not TOKEN:
        raise ValueError("Variable TOKEN manquante sur Railway")
    
    bot = telebot.TeleBot(TOKEN)
    
    threading.Thread(target=boucle_auto, daemon=True).start()
    start_polling()
