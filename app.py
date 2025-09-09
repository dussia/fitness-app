from flask import Flask, request, jsonify
import sqlite3, requests

BOT_TOKEN = "YOUR_BOT_TOKEN"
DB = "books.db"

app = Flask(__name__)

def get_file_url(file_id):
    resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}")
    data = resp.json()
    if "result" in data:
        return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{data['result']['file_path']}"
    return None

@app.route("/search")
def search():
    q = request.args.get("q", "")
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT title, author, genre, file_id FROM books WHERE title LIKE ? OR author LIKE ?", 
                (f"%{q}%", f"%{q}%"))
    results = []
    for title, author, genre, file_id in cur.fetchall():
        url = get_file_url(file_id) if file_id else None
        if url:
            results.append({"title": title, "author": author, "genre": genre, "url": url})
    conn.close()
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)