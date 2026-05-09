import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from openai import OpenAI
from PIL import Image
import pytesseract
from PyPDF2 import PdfReader

# ======================
# ВСТАВЬ СЮДА СВОИ НОВЫЕ КЛЮЧИ
# ======================

BOT_TOKEN = "8282429782:AAFlRUz-AsJ3YKHFy7ukWciLZAuWIIq09Yw"
OPENAI_API_KEY = "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"

# ======================

client = OpenAI(api_key=OPENAI_API_KEY)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# START
@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "🤖 AI бот запущен\n\n"
        "Отправь:\n"
        "- текст\n"
        "- фото\n"
        "- txt/log/pdf файл"
    )

# CHAT GPT
@dp.message(F.text)
async def chat(message: Message):
    if message.text.startswith("/"):
        return

    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": message.text}]
        )
        await message.answer(res.choices[0].message.content)

    except Exception as e:
        await message.answer(f"Ошибка: {e}")

# PHOTO OCR
@dp.message(F.photo)
async def photo(message: Message):
    file = await bot.get_file(message.photo[-1].file_id)
    path = file.file_path

    os.makedirs("photos", exist_ok=True)
    local = f"photos/{message.photo[-1].file_id}.jpg"

    await bot.download_file(path, local)

    img = Image.open(local)
    text = pytesseract.image_to_string(img, lang="rus+eng")

    await message.answer(f"📷 Текст:\n\n{text[:4000]}")

# FILES
@dp.message(F.document)
async def doc(message: Message):
    file = await bot.get_file(message.document.file_id)
    path = file.file_path

    os.makedirs("files", exist_ok=True)
    local = f"files/{message.document.file_name}"

    await bot.download_file(path, local)

    name = message.document.file_name.lower()

    if name.endswith(".txt") or name.endswith(".log"):
        with open(local, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

    elif name.endswith(".pdf"):
        reader = PdfReader(local)
        content = "".join([p.extract_text() or "" for p in reader.pages])

    else:
        await message.answer("Формат не поддерживается")
        return

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Анализируй файлы кратко и понятно"},
            {"role": "user", "content": content[:12000]}
        ]
    )

    await message.answer(res.choices[0].message.content[:4000])

# RUN
async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
