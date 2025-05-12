import requests
import hashlib
import time

URL = "https://mensa.jp/exam/"
WEBHOOK_URL = "https://discord.com/api/webhooks/1371494918744309820/qboT_2TRBYQCAwszKCWiY6-Lzvzuy_KUeBvcWFE9p1vE6-5GTGt2ZsspE3cBMjpfuCV9"
CHECK_INTERVAL = 300

def get_page_hash(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return hashlib.sha256(response.text.encode('utf-8')).hexdigest()
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

def monitor():
    print("🔍 mensa.jp/exam を監視中...")
    send_discord_notification("👋 監視プログラムが起動しました（テスト送信）")
    last_hash = get_page_hash(URL)
    while True:
        time.sleep(CHECK_INTERVAL)
        current_hash = get_page_hash(URL)
        if current_hash and current_hash != last_hash:
            send_discord_notification(f"🧠 MENSA試験ページが更新されました: {URL}")
            last_hash = current_hash
        else:
            print("✅ 変化なし")

if __name__ == "__main__":
    monitor()
