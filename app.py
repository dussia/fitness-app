from flask import Flask, request, jsonify
import requests

BOT_TOKEN = "8185115428:AAGzj8H8u-2i-iBV05WLxhr_rVnVwNC1PTs"  # вставь токен твоего бота
CHANNEL_ID = "@i_mir_tesen"   # юзернейм канала с аудиокнигами

app = Flask(__name__)

# Хранение сообщений в памяти (для упрощения)
books_cache = []

def get_file_url(file_id):
    """Получаем прямую ссылку на аудиофайл через Telegram API"""
    resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}")
    data = resp.json()
    if "result" in data:
        file_path = data["result"]["file_path"]
        return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    return None

def fetch_channel_messages():
    """Загружаем последние сообщения из канала через бота"""
    global books_cache
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    resp = requests.get(url)
    data = resp.json()
    books = []
    if "result" in data:
        for item in data["result"]:
            msg = item.get("message")
            if msg and "audio" in msg:
                text = msg.get("text", "Без названия")
                file_id = msg["audio"]["file_id"]
                url = get_file_url(file_id)
                books.append({
                    "title": text[:50],
                    "author": "Неизвестно",
                    "genre": "Разное",
                    "url": url
                })
    books_cache = books

# API для поиска
@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    if not books_cache:
        fetch_channel_messages()
    results = [b for b in books_cache if query in b["title"].lower() or query in b["author"].lower()]
    return jsonify(results)

if __name__ == "__main__":
    fetch_channel_messages()
    app.run(host="0.0.0.0", port=5000)