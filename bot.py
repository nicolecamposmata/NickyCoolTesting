import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

LIGAS = {
    "champions": 3,
    "la liga": 140,
    "premier": 152,
    "bundesliga": 130,
    "serie a": 132,
    "mls": 142,
    "primera division costa rica": 197,
}

def obtener_partidos_hoy():
    hoy = datetime.now().strftime("%Y-%m-%d")
    url = f"https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={hoy}&s=Soccer"
    resp = requests.get(url, timeout=10)
    data = resp.json()

    if not data.get("events"):
        return "No encontré partidos de fútbol para hoy 😕"

    lineas = ["⚽ *Partidos de hoy:*\n"]
    for evento in data["events"][:20]:
        local = evento.get("strHomeTeam", "?")
        visita = evento.get("strAwayTeam", "?")
        hora_utc = evento.get("strTime", "")
        liga = evento.get("strLeague", "Liga desconocida")
        
        hora_texto = f"🕐 {hora_utc} UTC" if hora_utc else "Hora no disponible"
        
        lineas.append(f"🏟 *{liga}*")
        lineas.append(f"   {local} vs {visita}")
        lineas.append(f"   {hora_texto}\n")

    return "\n".join(lineas)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! 👋 Soy tu bot de partidos de fútbol.\n\n"
        "Puedes preguntarme:\n"
        "• /partidos — Ver partidos de hoy\n"
        "• /ayuda — Ver todos los comandos"
    )

async def partidos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Buscando partidos... ⏳")
    resultado = obtener_partidos_hoy()
    await update.message.reply_text(resultado, parse_mode="Markdown")

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 *Comandos disponibles:*\n\n"
        "/partidos — Partidos de hoy\n"
        "/start — Mensaje de bienvenida\n\n"
        "También puedes escribir 'partidos' o 'qué hay hoy' y te respondo 🙂",
        parse_mode="Markdown"
    )

async def mensaje_libre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    if any(p in texto for p in ["partido", "partidos", "qué hay", "que hay", "hoy", "juegos", "fútbol"]):
        await partidos(update, context)
    else:
        await update.message.reply_text(
            "No entendí bien 😅 Escribe /partidos para ver los partidos de hoy."
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("partidos", partidos))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_libre))
    print("Bot corriendo...")
    app.run_polling()

if __name__ == "__main__":
    main()
