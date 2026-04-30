import os
import time
import requests
import telebot
from datetime import datetime

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = telebot.TeleBot(TOKEN)

# --- CONFIG IPA ---
MIN_IPA = 75 # % minimum de pression
MIN_XG_FAV = 1.30
MAX_XG_OUTSIDER = 0.50
MIN_SOT = 6 # Shots on target
CHECK_INTERVAL = 120 # Check toutes les 2 min

sent_alerts = set()

def get_live_matches():
    """Chope tous les matchs live Sofascore"""
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.json().get("events", [])
    except:
        return []

def get_match_stats(match_id):
    """Chope les stats live d'un match"""
    url = f"https://api.sofascore.com/api/v1/event/{match_id}/statistics"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.json()
    except:
        return {}

def get_match_incidents(match_id):
    """Chope le momentum/pressure chart"""
    url = f"https://api.sofascore.com/api/v1/event/{match_id}/graph"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.json()
    except:
        return {}

def check_ipa_80e(match):
    """Vérifie si le match match la strat IPA 80e"""
    match_id = match["id"]
    minute = match.get("time", {}).get("current", 0)
    
    # On check que entre 75e et 83e
    if minute < 75 or minute > 83:
        return None
    
    if match_id in sent_alerts:
        return None
    
    home_team = match["homeTeam"]["name"]
    away_team = match["awayTeam"]["name"]
    home_score = match["homeScore"]["current"]
    away_score = match["awayScore"]["current"]
    
    # Qui est favori? Basé sur cotes pre-match si dispo
    # Sinon on prend l'équipe à domicile par défaut
    fav_is_home = True # Simplification
    
    stats = get_match_stats(match_id)
    graph = get_match_incidents(match_id)
    
    if not stats or not graph:
        return None
    
    try:
        # 1. Chope l'IPA des 5 dernières minutes
        pressure_data = graph.get("graphPoints", [])
        if len(pressure_data) < 5:
            return None
            
        last_5_ipa = [p["value"] for p in pressure_data[-5:]]
        avg_ipa = sum(last_5_ipa) / 5
        
        if avg_ipa < MIN_IPA:
            return None
        
        # 2. Chope xG et Shots on Target
        stat_groups = stats.get("statistics", [])
        xg_home = xg_away = sot_home = sot_away = 0
        
        for group in stat_groups:
            if group["period"] == "ALL":
                for stat in group["groups"][0]["statisticsItems"]:
                    if stat["name"] == "Expected goals":
                        xg_home = float(stat["home"])
                        xg_away = float(stat["away"])
                    if stat["name"] == "Shots on target":
                        sot_home = int(stat["home"])
                        sot_away = int(stat["away"])
        
        # 3. Vérifie les conditions
        fav_xg = xg_home if fav_is_home else xg_away
        outsider_xg = xg_away if fav_is_home else xg_home
        fav_sot = sot_home if fav_is_home else sot_away
        fav_score = home_score if fav_is_home else away_score
        outsider_score = away_score if fav_is_home else home_score
        
        if fav_xg < MIN_XG_FAV:
            return None
        if outsider_xg > MAX_XG_OUTSIDER:
            return None
        if fav_sot < MIN_SOT:
            return None
        
        # 4. Check le score : 0-0 ou favori mène 1-0 ou favori mené 0-1
        valid_score = (fav_score == 0 and outsider_score == 0) or \
                      (fav_score == 1 and outsider_score == 0) or \
                      (fav_score == 0 and outsider_score == 1)
        
        if not valid_score:
            return None
        
        # C'EST BON, ALERTE!
        sent_alerts.add(match_id)
        
        return {
            "home": home_team,
            "away": away_team,
            "minute": minute,
            "score": f"{home_score}-{away_score}",
            "ipa": int(avg_ipa),
            "xg": f"{xg_home:.2f} - {xg_away:.2f}",
            "sot": f"{sot_home}-{sot_away}",
            "fav_team": home_team if fav_is_home else away_team,
            "situation": "0-0" if fav_score == 0 and outsider_score == 0 else 
                        "Mène 1-0" if fav_score > outsider_score else "Mené 0-1"
        }
        
    except Exception as e:
        print(f"Error match {match_id}: {e}")
        return None

def send_ipa_alert(data):
    msg = f"""
🔥 *ALERTE IPA 80E* 🔥

⚽ *{data['home']} vs {data['away']}*
⏱️ Minute: {data['minute']} | Score: {data['score']}

📊 *STATS CHAUDES:*
🔴 IPA 5min: {data['ipa']}% ✅
📈 xG: {data['xg']} ✅
🎯 Tirs cadrés: {data['sot']} ✅
👑 Situation: {data['fav_team']} {data['situation']}

💰 *PARI CONSEILLÉ:*
`But marqué 80-90 min : OUI` @2.60-3.80

⚡ Mise 3% bankroll max
⏳ Check si IPA reste >60% à 80e

*IPA 80E Sniper Bot*
"""
    
    sofascore_url = f"https://www.sofascore.com/event/{data['home']}-{data['away']}"
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📊 Voir Match Sofascore", url=sofascore_url))
    
    bot.send_message(CHAT_ID, msg, parse_mode="Markdown", reply_markup=markup)

def main():
    bot.send_message(CHAT_ID, "✅ *IPA 80E SNIPER BOT STARTED* ✅\n\nScan Sofascore toutes les 2 min...")
    
    while True:
        try:
            matches = get_live_matches()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Scan {len(matches)} matchs live...")
            
            for match in matches:
                alert = check_ipa_80e(match)
                if alert:
                    send_ipa_alert(alert)
                    time.sleep(2)
            
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            print(f"Erreur main: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
