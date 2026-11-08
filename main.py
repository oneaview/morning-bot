import os
import requests
import xml.etree.ElementTree as ET

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def get_news():
    url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    res = requests.get(url)
    root = ET.fromstring(res.content)
    items = root.findall(".//item")[:5]
    
    news_lines = []
    for item in items:
        title = item.find("title").text
        link = item.find("link").text
        news_lines.append(f"• <a href='{link}'>{title}</a>")
    return "\n\n".join(news_lines)

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    news = get_news()
    message = f"☀️ <b>[GitHub Actions 모닝 브리핑]</b>\n\n<b>🔥 실시간 헤드라인 뉴스 TOP 5</b>\n\n{news}"
    send_telegram(message)
