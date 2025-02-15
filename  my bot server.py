import telebot
import requests
import re
from telebot import types
from bs4 import BeautifulSoup

# ✅ إعدادات البوت
TOKEN = "8184423446:AAEDN300uiPu55Rf67_DzmifDAJVFk-5y5s"
bot = telebot.TeleBot(TOKEN)

# ✅ API لجلب الأخبار من CryptoPanic
CRYPTO_NEWS_API_KEY = "dd14d443e59ed970fcdfbc77e02df61d1a26beb1"
CRYPTO_NEWS_URL = f"https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTO_NEWS_API_KEY}&public=true"

# ✅ تخزين آخر البيانات لمنع التكرار
previous_airdrops = set()
previous_news = set()

# ✅ دالة تهريب MarkdownV2
def escape_markdown_v2(text):
    """ تهريب الرموز الخاصة في MarkdownV2 """
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(r'([{}])'.format(re.escape(escape_chars)), r'\\\1', text)

# ✅ دالة عرض القائمة الرئيسية
def show_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("/start", "/latest_airdrops", "/crypto_news", "/trade", "/portfolio", "/market_analysis", "/auto_tasks", "/wallet_manager",
               "/community", "/donate", "/faq", "/change_language", "/delete_wallet", "/add_wallet", "/convert_currency",
               "/auto_translate", "/stablecoins_support", "/smart_wallet_manager")
    bot.send_message(message.chat.id, "🔍 *اختياراتك:*", reply_markup=markup, parse_mode="MarkdownV2")

# ✅ أمر /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "مرحباً! أنا بوت الأيردروب. كيف يمكنني مساعدتك؟")
    show_main_menu(message)

# ✅ جلب أحدث الأيردروبز بدون تكرار
def fetch_airdrops():
    global previous_airdrops
    url = "https://airdrops.io/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        airdrops = soup.find_all("h3")

        result = []
        new_airdrops = set()

        for airdrop in airdrops:
            airdrop_name = escape_markdown_v2(airdrop.text.strip())
            airdrop_link = airdrop.find_parent("a")

            if airdrop_link and "href" in airdrop_link.attrs:
                airdrop_link = airdrop_link["href"]
            else:
                continue

            if airdrop_name not in previous_airdrops:  # تجنب التكرار
                new_airdrops.add(airdrop_name)
                result.append(f"🚀 *{airdrop_name}*\n🔗 [رابط الأيردروب]({airdrop_link})")

            if len(result) == 5:  # جلب 5 فقط
                break

        previous_airdrops.update(new_airdrops)  # تحديث القائمة السابقة

        return "\n\n".join(result) if result else "❌ لا توجد أيردروبز جديدة حالياً."
    else:
        return f"❌ فشل الاتصال بالموقع: {response.status_code}"

@bot.message_handler(commands=['latest_airdrops'])
def latest_airdrops(message):
    bot.send_message(message.chat.id, "⏳ جاري جلب أحدث الأيردروبز...")
    airdrop_data = fetch_airdrops()
    bot.send_message(message.chat.id, airdrop_data, parse_mode="MarkdownV2", disable_web_page_preview=True)

# ✅ جلب أحدث الأخبار بدون تكرار
def fetch_crypto_news():
    global previous_news
    response = requests.get(CRYPTO_NEWS_URL)

    if response.status_code == 200:
        data = response.json()
        articles = data.get("results", [])

        if not articles:
            return "❌ لا توجد أخبار حالياً."

        news_list = []
        new_news = set()

        for article in articles:
            title = escape_markdown_v2(article["title"])
            link = article["url"]

            if title not in previous_news:  # تجنب التكرار
                new_news.add(title)
                news_list.append(f"📰 *{title}*\n🔗 [اقرأ المزيد]({link})")

            if len(news_list) == 5:  # جلب 5 فقط
                break

        previous_news.update(new_news)  # تحديث القائمة السابقة

        return "\n\n".join(news_list) if news_list else "❌ لا توجد أخبار جديدة حالياً."
    else:
        return f"❌ فشل الاتصال بمصدر الأخبار: {response.status_code}"

@bot.message_handler(commands=['crypto_news'])
def crypto_news(message):
    bot.send_message(message.chat.id, "⏳ جاري جلب أحدث أخبار العملات الرقمية...")
    news_data = fetch_crypto_news()
    bot.send_message(message.chat.id, news_data, parse_mode="MarkdownV2", disable_web_page_preview=True)

# 🚧 الميزات قيد التطوير
@bot.message_handler(commands=['trade', 'portfolio', 'market_analysis', 'auto_tasks', 'wallet_manager',
                               'community', 'donate', 'faq', 'change_language', 'delete_wallet', 'add_wallet',
                               'convert_currency', 'auto_translate', 'stablecoins_support', 'smart_wallet_manager'])
def under_development(message):
    bot.send_message(message.chat.id, "🚧 هذه الميزة قيد التطوير حالياً!")

# ✅ تشغيل البوت بشكل مستمر
if __name__ == "__main__":
    bot.polling(none_stop=True)