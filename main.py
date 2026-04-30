import os
import time
import telebot
from datetime import datetime
import requests

TOKEN = os.getenv 8699033001:AAGhYLpSrpm79HebzovzqFwZSvCrNK-3T3c
CHAT_ID = os.getenv 7661174841
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
        status = event['status']
        if status['type'] != 'inprogress':
            return None
            
        minute_str = status.get('description', '0').replace("'", "")
        if not minute_str.isdigit():
            return None
            
        minute = int(minute_str)
        home_score = event['homeScore']['current']
        away_score = event['awayScore']['current']
        
        # V6 LIVE: 0-0 après 78min = BUT SUPPLÉMENTAIRE EN FEU
        if home_score == 0 and away_score == 0 and minute >= 78:
            home_team = event['homeTeam']['name']
            away_team = event['awayTeam']['name']
            tournament = event['tournament']['name']
            
            message = f"⚽ V6 LIVE BUT {minute}'\n\n" \
                     f"🏆 {tournament}\n" \
                     f"🔥 {home_team} 0-0 {away_team}\n\n" \
                     f"SNIPER : +0.5 BUT / Prochain But\n" \
                     f"Cote en feu sur 1xBet. GO GO!"
            return message
            
    except Exception as e:
        print(f"Erreur event: {e}")
        return None

def main():
    bot.send_message(CHAT_ID, "✅ Bot V6 LIVE BUT démarré. Scan 0-0 après 78e min pour Over 0.5.")
    sent_matches = set()
    
    while True:
        print(f"Scan live {datetime.now().strftime('%H:%M:%S')}")
        matches = get_live_matches()
        
        for match in matches:
            match_id = match['id']
            if match_id in sent_matches:
                continue
                
            alert = check_v6_live_but(match)
            if alert:
                bot.send_message(CHAT_ID, alert)
                sent_matches.add(match_id)
                print(f"BUT ALERTE: {match['homeTeam']['name']} vs {match['awayTeam']['name']}")
        
        time.sleep(60)

if __name__ == "__main__":
    main()
