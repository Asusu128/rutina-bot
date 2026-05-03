import os
import telebot
import schedule
import time
import threading
from datetime import datetime

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

users = {}

def get_user(uid):
    if uid not in users:
        users[uid] = {"turno": "", "streak": 0}
    return users[uid]

def limpieza_del_dia():
    tareas = ["cocina", "baño", "habitación", "salón", "orden general"]
    return tareas[datetime.now().weekday() % len(tareas)]

def rutina_gym(streak):
    if streak < 3:
        return "Full body"
    elif streak < 6:
        return "Torso / Pierna"
    else:
        return "Push / Pull / Legs"

def plan(turno, streak):
    limpieza = limpieza_del_dia()
    gym = rutina_gym(streak)

    if "8-14" in turno:
        base = "Gym por la tarde"
    elif "15-22" in turno:
        base = "Gym por la mañana"
    elif "libre" in turno:
        base = "Gym completo + extra"
    else:
        base = "Día flexible"

    return f"""🔥 PLAN DE HOY
💪 Gym: {base} ({gym})
🧹 Limpieza: {limpieza}
🧠 Hábitos: 1h productiva

👉 Responde HECHO o NO por la noche
"""

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🔥 Rutina Letal activada\nUsa /hoy 8-14, /hoy 15-22 o /hoy libre")

@bot.message_handler(commands=['hoy'])
def hoy(m):
    uid = m.chat.id
    user = get_user(uid)

    turno = m.text.replace("/hoy", "").strip().lower()
    user["turno"] = turno

    bot.send_message(uid, plan(turno, user["streak"]))

def check_noche():
    for uid, user in users.items():
        bot.send_message(uid, "🌙 ¿Has cumplido hoy? (HECHO / NO)")

schedule.every().day.at("22:30").do(check_noche)

@bot.message_handler(func=lambda m: m.text.lower() == "hecho")
def hecho(m):
    u = get_user(m.chat.id)
    u["streak"] += 1
    bot.reply_to(m, f"🔥 Racha: {u['streak']} días")

@bot.message_handler(func=lambda m: m.text.lower() == "no")
def no(m):
    u = get_user(m.chat.id)
    u["streak"] = 0
    bot.reply_to(m, "💀 Racha reiniciada. Mañana sin excusas.")

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_schedule, daemon=True).start()

bot.infinity_polling()
