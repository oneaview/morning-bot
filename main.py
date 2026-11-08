import os
import urllib.parse
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def get_korea_date():
    now = datetime.now()
    days = ["월", "화", "수", "목", "금", "토", "일"]
    return f"{now.strftime('%Y.%m.%d')} ({days[now.weekday()]})"

# 1. 날씨 & 옷차림 추천
def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=37.5665&longitude=126.9780&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=Asia%2FSeoul"
        data = requests.get(url, timeout=5).json()
        min_t = round(data['daily']['temperature_2m_min'][0])
        max_t = round(data['daily']['temperature_2m_max'][0])
        rain = data['daily']['precipitation_probability_max'][0]

        if rain >= 50:
            outfit = "☔ 비 소식이 있습니다. 우산을 꼭 챙기세요!"
        elif max_t >= 28:
            outfit = "☀️ 무더운 날씨입니다. 린넨, 반팔 등 통풍이 잘되는 옷을 입으세요."
        elif max_t >= 20:
            outfit = "🌿 활동하기 쾌적한 날씨입니다. 셔츠나 가벼운 가디건이 좋습니다."
        elif max_t >= 10:
            outfit = "🧥 일교차가 큽니다. 자켓, 가디건, 도톰한 외투를 챙기세요."
        else:
            outfit = "🧣 쌀쌀한 날씨입니다. 패딩이나 코트, 목도리를 추천합니다."

        return f"• 서울 {min_t}℃ ~ {max_t}℃ (강수확률 {rain}%)\n• 👔 <b>스타일 팁:</b> {outfit}"
    except Exception:
        return "• 날씨 정보를 가져오지 못했습니다."

# 2. 환율 (달러, 엔화, 유로, 위안화) 및 비트코인
def get_finance():
    fin_text = []
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5).json()
        krw = r['rates']['KRW']
        usd = round(krw)
        jpy = round((krw / r['rates']['JPY']) * 100)
        eur = round(krw / r['rates']['EUR'])
        cny = round(krw / r['rates']['CNY'])
        
        fin_text.append(f"• 💵 <b>달러(USD):</b> {usd:,}원 | 💴 <b>엔화(100엔):</b> {jpy:,}원")
        fin_text.append(f"• 💶 <b>유로(EUR):</b> {eur:,}원 | 🇨🇳 <b>위안화(CNY):</b> {cny:,}원")
    except Exception:
        pass
    try:
        c = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,krw", timeout=5).json()
        btc_krw = round(c['bitcoin']['krw'])
        btc_usd = round(c['bitcoin']['usd'])
        fin_text.append(f"• 🪙 <b>비트코인:</b> {btc_krw:,}원 (${btc_usd:,})")
    except Exception:
        pass
    return "\n".join(fin_text) if fin_text else "• 금융 정보를 불러오지 못했습니다."

# 3. 뉴스 10개 (양극재/음극재 투자 3개 + 트렌드/비즈니스 레퍼런스 7개)
def get_custom_news():
    news_blocks = []
    
    # 3-1. 양극재/음극재 투자 기사 3개
    try:
        query = urllib.parse.quote("양극재 OR 음극재 투자")
        url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
        res = requests.get(url, timeout=5)
        root = ET.fromstring(res.content)
        items = root.findall(".//item")[:3]
        
        battery_lines = ["🔋 <b>배터리 소재·투자 픽 (양극재/음극재)</b>"]
        for it in items:
            title = it.find("title").text.replace("<", "&lt;").replace(">", "&gt;")
            link = it.find("link").text
            battery_lines.append(f"• <a href='{link}'>{title}</a>")
        news_blocks.append("\n".join(battery_lines))
    except Exception:
        pass

    # 3-2. 경제/산업 트렌드 레퍼런스 (4개)
    trend_lines = ["🌐 <b>트렌드 & 산업 레퍼런스 픽 (7)</b>"]
    try:
        url_biz = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko"
        res_biz = requests.get(url_biz, timeout=5)
        root_biz = ET.fromstring(res_biz.content)
        for it in root_biz.findall(".//item")[:4]:
            title = it.find("title").text.replace("<", "&lt;").replace(">", "&gt;")
            link = it.find("link").text
            trend_lines.append(f"• [경제/산업] <a href='{link}'>{title}</a>")
    except Exception:
        pass

    # 3-3. IT/신기술 트렌드 레퍼런스 (3개)
    try:
        url_tech = "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ko&gl=KR&ceid=KR:ko"
        res_tech = requests.get(url_tech, timeout=5)
        root_tech = ET.fromstring(res_tech.content)
        for it in root_tech.findall(".//item")[:3]:
            title = it.find("title").text.replace("<", "&lt;").replace(">", "&gt;")
            link = it.find("link").text
            trend_lines.append(f"• [테크/혁신] <a href='{link}'>{title}</a>")
    except Exception:
        pass

    if len(trend_lines) > 1:
        news_blocks.append("\n".join(trend_lines))

    return "\n\n".join(news_blocks) if news_blocks else "• 뉴스를 불러오지 못했습니다."

# 4. IT & 테크 핫 트렌드 (GeekNews)
def get_geeknews():
    try:
        url = "https://news.hada.io/rss/news"
        res = requests.get(url, timeout=5)
        root = ET.fromstring(res.content)
        items = root.findall(".//item")[:2]
        lines = []
        for it in items:
            title = it.find("title").text.replace("<", "&lt;").replace(">", "&gt;")
            link = it.find("link").text
            lines.append(f"• <a href='{link}'>{title}</a>")
        return "\n".join(lines)
    except Exception:
        return "• 테크 트렌드를 불러오지 못했습니다."

# 5. 오늘의 깃허브 실시간 인기 오픈소스
def get_github_trending():
    try:
        url = "https://api.github.com/search/repositories?q=stars:>1000+pushed:>2024-01-01&sort=updated&order=desc"
        res = requests.get(url, timeout=5, headers={"User-Agent": "MorningBot"}).json()
        repo = res['items'][0]
        name = repo['full_name']
        desc = (repo['description'] or "설명 없음")[:60]
        url = repo['html_url']
        stars = repo['stargazers_count']
        return f"• <a href='{url}'><b>{name}</b></a> (⭐ {stars:,})\n  ↳ <i>{desc}...</i>"
    except Exception:
        return "• 깃허브 트렌드를 불러오지 못했습니다."

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
    date_str = get_korea_date()
    weather = get_weather()
    finance = get_finance()
    news = get_custom_news()
    geeknews = get_geeknews()
    github_trend = get_github_trending()

    message = (
        f"🏛️ <b>CHRIS DAILY INTELLIGENCE</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🗓️ <b>{date_str} | Morning Edition</b>\n\n"
        f"⛅ <b>오늘의 날씨 & 스타일 팁</b>\n{weather}\n\n"
        f"📊 <b>글로벌 모닝 마켓</b>\n{finance}\n\n"
        f"{news}\n\n"
        f"💡 <b>테크 & 트렌드 (GeekNews)</b>\n{geeknews}\n\n"
        f"🚀 <b>오늘의 깃허브 1위 픽</b>\n{github_trend}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"☕ <i>\"단순함이 궁극의 정교함이다.\" - 레오나르도 다빈치</i>"
    )

    send_telegram(message)
