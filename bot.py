import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import ClientSession

# Замените на токен вашего бота, полученный от BotFather
import os
TOKEN = os.getenv("TOKEN")

# Инициализация бота и диспетчера (aiogram 3.x)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_command(message: types.Message):
    """
    Обработчик команды /start.
    Отправляет приветственное сообщение.
    """
    await message.answer(
        "👋 Привет! Я GeoFinderBot.\n"
        "Отправь мне любой адрес, и я верну тебе его координаты (широту и долготу)."
    )

@dp.message()
async def handle_address(message: types.Message):
    """
    Обрабатывает любое входящее сообщение как адрес,
    отправляет запрос к Nominatim и возвращает координаты.
    """
    address = message.text.strip()
    if not address:
        await message.answer("❗ Пожалуйста, отправь непустой адрес.")
        return

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        # Укажите реальный email в User-Agent согласно политике Nominatim
        "User-Agent": "GeoFinderBot/1.0 (your_email@example.com)"
    }

    try:
        async with ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as resp:
                if resp.status != 200:
                    await message.answer("❌ Ошибка при обращении к сервису геокодирования.")
                    return

                data = await resp.json()
                if not data:
                    await message.answer("🔍 Адрес не найден. Попробуйте другой запрос.")
                    return

                lat = data[0].get("lat")
                lon = data[0].get("lon")
                display_name = data[0].get("display_name", address)

                osm_link = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}"
                await message.answer(
                    f"📍 Найдено: {display_name}\n"
                    f"Широта: `{lat}`\n"
                    f"Долгота: `{lon}`\n"
                    f"[Открыть на карте]({osm_link})",
                    parse_mode="Markdown"
                )
    except Exception as e:
        await message.answer(f"⚠️ Произошла ошибка: {e}")

async def main():
    """
    Точка входа: запускает опрос (polling) бота.
    """
    print("🤖 Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())