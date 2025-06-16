import telebot
import os
import base64
import mimetypes

# Импортируем наши ключи из файла config.py
from config import TELEGRAM_BOT_TOKEN, SAMBANOVA_API_KEY

# Импортируем инструменты для работы с ИИ
from langchain_sambanova import ChatSambaNovaCloud
from langchain_core.messages import HumanMessage

# --- Инициализация ---
print("Проверяем ключи...")
if not TELEGRAM_BOT_TOKEN or not SAMBANOVA_API_KEY:
    raise ValueError("Ошибка: Не найдены API-ключи в файле config.py!")

print("Ключи найдены. Запускаем бота и подключаемся к ИИ...")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
ai_model = ChatSambaNovaCloud(
    model="Llama-4-Maverick-17B-128E-Instruct",
    sambanova_api_key=SAMBANOVA_API_KEY
)

print("Бот и ИИ готовы к работе!")


# --- Логика работы с ИИ ---
def generate_description(image_path: str) -> str:
    """Отправляет фото в ИИ и получает текстовое описание."""
    try:
        # Финальный, самый точный промпт для ИИ, без лишних заголовков
        prompt_text = """You are a top-tier SEO specialist and creative copywriter for TikTok and Instagram Reels. Your mission is to create viral content about the climate crisis and its solutions.

Analyze the provided screenshot and create content that engages audiences, is optimized for search, and promotes important ideas about climate and solutions.

Generate the following elements integrated into a natural social media post:
1. A bright, catchy headline for the video in English for the cover, with a date, appearing as the first line of the post.
2. SEO-optimized description for the video in English, with emojis, naturally following the headline.
3. A short explanation with a solution (if the video contains info content), integrated into the description. Include details of the country and the type of climate disaster depicted from the photo.
4. 5-10 relevant hashtags, appearing at the very end of the post.

Always mention the 12,000-year climate cycle, Allatra scientists, and that a climate report is available via link in bio. Use emojis in the description.

Emphasize that solutions already exist, such as controlled volcanic degassing, water-from-air generators, and other suppressed technologies.

The entire response should be in English, ready for copying, without unnecessary information.
**CRITICAL: The response should NOT include the words "COUNTRY", "CLIMATE EVENT", "DESCRIPTION", "Headline:", "Context/Solution:", or any other section headers.** The text must flow naturally as a single, coherent social media post, ending with hashtags.

Example format (this is just a guide, the content should be based on the analyzed image):
Severe hailstorm slams Tunisia — May 7, 2025 ⚡❄️
Massive hail and heavy rain devastated crops across Kef, hitting Sakiet Sidi Youssef, West Kef, East Kef, and Sers. Fields were shredded, roads flooded, locals in shock.

But hey — this isn't just "bad weather." Scientists in the AllatRa report (check my bio!) warn about the 12,000-year cycle of planetary cataclysms 🌍⚠️.
We're not just watching climate change — we're watching Earth's clock tick. Solutions like controlled volcanic degassing and water-from-air generators already exist.

Stay alert. Stay sharp. This is just the beginning. 💥

#Tunisia #Kef #Hailstorm #CropDamage #ExtremeWeather #12000YearCycle #AllatRa #ClimateCrisis #GlobalWakeUp #PlanetAlert #NaturePower

Based on the screenshot I'm analyzing, create content in exactly this format."""

        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        mime_type = mimetypes.guess_type(image_path)[0] or 'image/jpeg'

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}},
            ]
        )
        
        response = ai_model.invoke([message])
        return response.content

    except Exception as e:
        print(f"ОШИБКА при обращении к ИИ: {e}")
        return "К сожалению, произошла ошибка при генерации описания. Попробуйте позже."


# --- Обработчики сообщений Telegram ---
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, 'Привет! Отправь мне скриншот, и я создам для него описание.')

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "Фото получил. Генерирую описание, это может занять до минуты...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_path = 'temp_photo.jpg'
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        description = generate_description(image_path)
        bot.reply_to(message, f"Готово!\n\n{description}")
        os.remove(image_path)
    except Exception as e:
        print(f"ОШИБКА при обработке фото: {e}")
        bot.reply_to(message, "Произошла ошибка при обработке вашего фото.")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    bot.reply_to(message, 'Пожалуйста, отправь мне фото (скриншот).')


# --- Запуск бота ---
print('Для остановки бота нажмите Ctrl+C')
bot.polling()
