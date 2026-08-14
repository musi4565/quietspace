"""QuietSpace Tashkent Telegram boti (demo)."""

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from api import ai_chat, confirm_link, search_places
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

MAIN_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔎 Joylarni qidirish"), KeyboardButton(text="🤖 AI bilan topish")],
        [KeyboardButton(text="🔗 Hisobni bog'lash"), KeyboardButton(text="❓ Yordam")],
    ],
    resize_keyboard=True,
)


class Flow(StatesGroup):
    search_text = State()
    ai_text = State()
    link_code = State()


def price_label(price: int) -> str:
    if price == 0:
        return "Bepul"
    return f"{price:,} so'm".replace(",", " ")


def place_line(p: dict, i: int) -> str:
    line = (
        f"{i}. {p['name']}\n"
        f"📍 {p['district_name']} · 🤫 {p['noise_display']} · 📶 {p['wifi_speed']} Mbps\n"
        f"💰 {price_label(p['price_per_hour'])} · 🟢 {p['available_slots']} ta bo'sh"
    )
    if p.get("avg_rating"):
        line += f"\n⭐ {float(p['avg_rating']):.1f}"
    return line


async def send_places(message: Message, results: list) -> None:
    if not results:
        await message.answer("Hech narsa topilmadi 😔 Boshqa so'z bilan urinib ko'ring.")
        return
    parts = []
    for i, p in enumerate(results[:5], 1):
        parts.append(place_line(p, i))
    await message.answer("\n\n".join(parts))


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Salom! 🌿 Men QuietSpace Tashkent botiman.\n\n"
        "Men yordamida shahardagi jimjit, Wi-Fi va rozetkasi bor joylarni topishingiz mumkin.\n\n"
        "Quyidagilardan birini tanlang:",
        reply_markup=MAIN_KB,
    )


@dp.message(Command("help"))
@dp.message(F.text == "❓ Yordam")
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Mendan foydalanish:\n\n"
        "🔎 Joylarni qidirish — nom, tuman yoki manzil bo'yicha qidiraman.\n"
        "🤖 AI bilan topish — talabingizni tabiiy tilda yozing, masalan:\n"
        "   \"Chilonzorda tinch, rozetkasi bor joy qani?\"\n"
        "🔗 Hisobni bog'lash — saytdagi hisobingizni Telegram bilan bog'laydi.\n\n"
        "Bot: @QuietSpaceBot (demo)",
        reply_markup=MAIN_KB,
    )


@dp.message(F.text == "🔎 Joylarni qidirish")
async def ask_search(message: Message, state: FSMContext) -> None:
    await state.set_state(Flow.search_text)
    await message.answer("Nima qidiryapsiz? (nom, tuman, manzil)")


@dp.message(Flow.search_text)
async def do_search(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        data = await search_places(message.text)
        await send_places(message, data.get("results", []))
    except Exception as exc:
        logger.exception("search failed")
        await message.answer(f"Xatolik yuz berdi: {exc}")


@dp.message(F.text == "🤖 AI bilan topish")
async def ask_ai(message: Message, state: FSMContext) -> None:
    await state.set_state(Flow.ai_text)
    await message.answer("Talabingizni yozing, masalan:\n\"Yunusobodda tinch, 50 mingdan kam joy\"")


@dp.message(Flow.ai_text)
async def do_ai(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("🤔 Tahlil qilmoqdaman...")
    try:
        data = await ai_chat(message.text)
        text = data.get("message", "")
        if len(text) > 4000:
            text = text[:3900] + "..."
        await message.answer(text)
        for item in data.get("results", [])[:3]:
            p = item["place"]
            url = f"https://t.me/share/url?url={p['name']}"
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{item['match_percent']}% mos — {p['name']}",
                            url=url,
                        )
                    ]
                ]
            )
            await message.answer(place_line(p, 1), reply_markup=kb)
    except Exception as exc:
        logger.exception("ai failed")
        await message.answer(f"Xatolik yuz berdi: {exc}")


@dp.message(F.text == "🔗 Hisobni bog'lash")
async def ask_link(message: Message, state: FSMContext) -> None:
    await state.set_state(Flow.link_code)
    await message.answer(
        "1. quietspace.uz saytida profil sahifasiga o'ting.\n"
        "2. «Telegram bilan bog'lash» tugmasini bosing — kod olasiz.\n"
        "3. Shu kodni menga yuboring."
    )


@dp.message(Command("link"))
async def cmd_link(message: Message, state: FSMContext) -> None:
    parts = message.text.split()
    if len(parts) < 2:
        await ask_link(message, state)
        return
    await state.clear()
    await do_link(message, parts[1])


@dp.message(Flow.link_code)
async def flow_link(message: Message, state: FSMContext) -> None:
    await state.clear()
    await do_link(message, message.text.strip())


async def do_link(message: Message, code: str) -> None:
    try:
        result = await confirm_link(code, message.chat.id, message.from_user.username or "")
        if result.get("success"):
            await message.answer(f"✅ Hisob bog'landi: {result.get('user_email', '')}")
        else:
            await message.answer(f"❌ {result.get('message', 'Kod notogri')}")
    except Exception as exc:
        logger.exception("link failed")
        await message.answer(f"Xatolik yuz berdi: {exc}")


@dp.message()
async def fallback(message: Message) -> None:
    await message.answer("Tushunmadim 🤔 Quyidagi tugmalardan birini tanlang:", reply_markup=MAIN_KB)


async def main() -> None:
    me = await bot.get_me()
    logger.info("Bot ishga tushdi: @%s (%s)", me.username, me.full_name)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())