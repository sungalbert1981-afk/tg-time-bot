import os
import time
import requests
from datetime import datetime, timedelta, timezone

# 設定台灣時區 (UTC+8)
TAIWAN_TZ = timezone(timedelta(hours=8))

# 從環境變數讀取敏感資訊（或直接在此替換成您的真實資訊）
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "您的真實BOT_TOKEN")
# 頻道 Chat ID 格式通常為 -100xxxxxxxxxx
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "您的真實頻道CHAT_ID")

def send_hourly_broadcast():
    """執行整點報時發送"""
    now = datetime.now(TAIWAN_TZ)
    hour = now.hour
    
    # 組合報時訊息
    message = f"🔔 【整點報時】現在時間是台北時間 {hour:02d}:00"
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        if result.get("ok"):
            print(f"[{datetime.now(TAIWAN_TZ).strftime('%Y-%m-%d %H:%M:%S')}] 報時成功: {hour}點")
        else:
            print(f"發送失敗，錯誤訊息: {result.get('description')}")
    except Exception as e:
        print(f"發送時發生異常: {e}")

def wait_until_next_hour():
    """計算精準等待時間，直到下一個整點的第 0 秒"""
    now = datetime.now(TAIWAN_TZ)
    # 計算下一個整點
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    # 計算需要等待的秒數
    sleep_seconds = (next_hour - now).total_seconds()
    return sleep_seconds

def main():
    print(f"=== Telegram 整點報時機器人已啟動 ===")
    print(f"目標頻道 ID: {CHAT_ID}")
    print(f"目前時間: {datetime.now(TAIWAN_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 啟動時先檢查連線狀況
    url = f"https://api.telegram.org/bot{TOKEN}/getMe"
    try:
        res = requests.get(url, timeout=10).json()
        if not res.get("ok"):
            print("⚠️ 警告: Bot Token 驗證失敗，請檢查 Token 是否正確！")
    except Exception:
        pass

    while True:
        sleep_time = wait_until_next_hour()
        print(f"等待下一次報時中... 剩餘 {int(sleep_time)} 秒")
        # 為了避免長時間 sleep 造成環境異常或中斷，採取分段 sleep
        while sleep_time > 60:
            time.sleep(60)
            sleep_time = wait_until_next_hour()
        
        # 精準微調最後幾秒
        if sleep_time > 0:
            time.sleep(sleep_time)
            
        # 到達整點，執行報時
        send_hourly_broadcast()
        # 執行完後稍微暫停 2 秒，避免極短時間內重複觸發
        time.sleep(2)

if __name__ == "__main__":
    main()
