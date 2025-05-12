from flask import Flask, request, jsonify
import requests
import hashlib
import time
import threading
import os
from bs4 import BeautifulSoup

# ====== 設定 ======
URL = "https://mensa.jp/exam/"
WEBHOOK_URL = "https://discord.com/api/webhooks/1371494918744309820/qboT_2TRBYQCAwszKCWiY6-Lzvzuy_KUeBvcWFE9p1vE6-5GTGt2ZsspE3cBMjpfuCV9"
CHECK_INTERVAL = 300  # 秒

app = Flask(__name__)
monitoring = False
last_kanto_hash = None

def get_kanto_section_hash(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # HTML解析
        soup = BeautifulSoup(response.text, 'html.parser')

        # 関東地方の部分を探す（仮に "関東地方" というテキストを含むdivを探す）
        kanto_section = None
        for section in soup.find_all(['div', 'section', 'table', 'li']):
            if "関東" in section.get_text():
                kanto_section = section
                break

        if kanto_section:
            # 関東部分のHTMLからハッシュ生成
            return hashlib.sha256(kanto_section.encode('utf-8')).hexdigest()
        else:
            print("[⚠️] 関東地方の情報が見つかりませんでした")
            return None

    except Exception as e:
        print(f"[エラー] ページ取得失敗: {e}")
        return None

def send_discord_notification(message):
    data = {"content": message}
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        response.raise_for_status()
        print("[✅] Discordへ送信完了:", message)
    except Exception as e:
        print(f"[エラー] Discord通知失敗: {e}")

def monitor_loop():
    global monitoring, last_kanto_hash
    print("🔍 mensa.jp/exam 関東地方のみを監視中...")
    send_discord_notification("👋 Render監視Botが起動しました（関東地方のみ対象）")
    
    last_kanto_hash = get_kanto_section_hash(URL)
    while monitoring:
        time.sleep(CHECK_INTERVAL)
        current_hash = get_kanto_section_hash(URL)
        if current_hash and current_hash != last_kanto_hash:
            send_discord_notification(f"🧠 MENSA試験ページの関東地方が更新されました: {URL}")
            last_kanto_hash = current_hash
        else:
            print("✅ 関東地方に変化なし")

# ==== Flask API ====
@app.route("/")
def index():
    return "👋 関東地方のMENSA試験情報を監視中"

@app.route("/start", methods=["POST"])
def start_monitoring():
    global monitoring
    if not monitoring:
        monitoring = True
        thread = threading.Thread(target=monitor_loop)
        thread.start()
        return jsonify({"status": "監視開始"})
    else:
        return jsonify({"status": "すでに監視中"})

@app.route("/stop", methods=["POST"])
def stop_monitoring():
    global monitoring
    monitoring = False
    return jsonify({"status": "監視停止"})

@app.route("/check", methods=["GET"])
def manual_check():
    global last_kanto_hash
    current_hash = get_kanto_section_hash(URL)
    if current_hash != last_kanto_hash:
        send_discord_notification(f"🧠 関東地方が手動チェックで変更されました: {URL}")
        last_kanto_hash = current_hash
        return jsonify({"status": "更新あり"})
    else:
        return jsonify({"status": "変化なし"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render用
    app.run(host="0.0.0.0", port=port)
