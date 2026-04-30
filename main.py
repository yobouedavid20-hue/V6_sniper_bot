import os
import time
import telebot
from datetime import datetime
import requests

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = telebot.TeleBot(TOKEN)

def get_live_matches():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json().get('events', [])
    except:
        return []

def check_v6_live_but(event):
    try:
        if event['status']['type'] != 'inprogress':
            return None
            
        minute = int(event['status'].get('description', '0').replace("'", ""))
        home_score = event['homeScore']['current']
        away_score = event['awayScore']['current']
        
        if home_score == 0 and away_score == 0 and minute >= 78:
            home = event['homeTeam']['name']
            away = event['awayTeam']['name']
            league = event['tournament']['name']
            
            msg = f"⚽ V6 LIVE {minute}'\n\n🏆 {league}\n🔥 {home} 0-0 {away}\n\nSNIPER 1XBET :\n→ +0.5 BUT FT\n→ Prochain But\n\nGO SUR 1XBET CI DIRECT !"
            return msg
    except:
        return None

def main():
    bot.send_message(CHAT_ID, "✅ Bot V6 LIVE 1XBET démarré. Scan 0-0 après 78e.")
    sent_matches = set()
    
    while True:
        print(f"Scan {datetime.now().strftime('%H:%M:%S')}")
        matches = get_live_matches()
        
        for match in matches:
            if match['id'] in sent_matches:
                continue
                
            alert = check_v6_live_but(match)
            if alert:
                bot.send_message(CHAT_ID, alert)
                sent_matches.add(match['id'])
        
        time.sleep(60)

if __name__ == "__main__":
    main()
