"""QuietSpace Tashkent Telegram boti (demo, Aiogram 3).

Arxitektura: Telegram -> Aiogram -> Django API -> PostgreSQL
"""

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

from api import (
    ai_chat,
    confirm_link,
    get_districts,
    get_favorites,
    get_place,
    nearby_places,
    search_places,
    toggle_notifications,
)
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

MAIN_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔎 Joy topish"), KeyboardButton(text="🤖 AI orqali topish")],
        [KeyboardButton(text="🗺️ Yaqin joylar"), KeyboardButton(text="❤️ Sevimlilar")],
        [KeyboardButton(text="🔔 Bildirishnomalar"), KeyboardButton(text="🔗 Hisobni bog'lash")],
        [KeyboardButton(text="❓ Yordam")],
    ],
    resize_keyboard=True,
)

LOCATION_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📍 Joylashuvni yuborish", request_location=True)]],
    resize_keyboard=True,
)


class Flow(StatesGroup):
    search_district = State()
    search_noise = State()
    search_price = State()
    search_wifi = State()
    search_socket = State()
    ai_text = State()
    link_code = State()


NOISE_CHOICES = [
    ("Juda tinch", "very_quiet"),
    ("Tinch", "quiet"),
    ("O'rtacha", "average"),
    ("Shovqinli", "noisy"),
]
PRICE_CHOICES = [
    ("Bepul", "free"),
    ("50 mingdan kam", "under_50k"),
    ("100 mingdan kam", "under_100k"),
]
WIFI_CHOICES = [
    ("Yaxshi (20+ Mbps)", "good"),
    ("A'lo (50+ Mbps)", "excellent"),
]
YES_NO_CHOICES = [("Ha", "true"), ("Yo'q", "false")]


def skip_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⏭️ O'tkazib yuborish", callback_data="skip")]]
    )


def choice_kb(choices):
    rows = [[InlineKeyboardButton(text=label, callback_data=f"val:{value}")] for label, value in choices]
    rows.append([InlineKeyboardButton(text="⏭️ O'tkazib yuborish", callback_data="skip")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def price_label(price: int) -> str:
    if price == 0:
        return "Bepul"
    return f"{price:,} so'm".replace(",", " ")


def place_line(p: dict, i: int) -> str:
    line = (
        f"{i}. {p['name']} (ID: {p['id']})\n"
        f"📍 {p['district_name']} · 🤫 {p['noise_display']} · 📶 {p['wifi_speed']} Mbps\n"
        f"🔌 {'Bor' if p['socket_count'] else "Yo'q"} · 💰 {price_label(p['price_per_hour'])}"
        f" · 🟢 {p['available_slots']} ta bo'sh"
    )
    if p.get("avg_rating"):
        line += f"\n⭐ {float(p['avg_rating']):.1f}"
    if p.get("distance_km") is not None:
        line += f"\n📍 {float(p['distance_km']):.1f} km uzoqlikda"
    return line


async def send_places(message: Message, results: list, extra: str = "") -> None:
    if not results:
        await message.answer("Hech narsa topilmadi 😔 Boshqa so'z yoki filter bilan urinib ko'ring.")
        return
    parts = [extra] if extra else []
    parts.extend(place_line(p, i) for i, p in enumerate(results[:5], 1))
    await message.answer("\n\n".join(parts))
    await message.answer("Batafsil: /place <ID> buyrug'ini yuboring.")


# ---------------------------------------------------------------------------
# /start va umumiy
# ---------------------------------------------------------------------------
@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Salom! 🌿 Men QuietSpace Tashkent botiman.\n\n"
        "Menga shahardagi jimjit, Wi-Fi va rozetkasi bor ish joylarini topishda yordam beraman.\n\n"
        "Tanlang:",
        reply_markup=MAIN_KB,
    )


@dp.message(Command("help"))
@dp.message(F.text == "❓ Yordam")
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Mendan foydalanish:\n\n"
        "🔎 Joy topish — tuman, shovqin, narx, Wi-Fi va rozetka bo'yicha filterlab topaman.\n"
        "🤖 AI orqali topish — talabingizni tabiiy tilda yozing:\n"
        "   \"Chilonzorda tinch, rozetkasi bor joy qani?\"\n"
        "🗺️ Yaqin joylar — joylashuvingizni yuboring, eng yaqin joylarni ko'rsataman.\n"
        "❤️ Sevimlilar — bog'langan hisobning sevimli joylari.\n"
        "🔔 Bildirishnomalar — yangi mos joylar haqida xabar yoqish/o'chirish.\n"
        "🔗 Hisobni bog'lash — sayt hisobini Telegram bilan ulash.\n\n"
        "/place <ID> — joy haqida batafsil.",
        reply_markup=MAIN_KB,
    )


@dp.message(Command("place"))
async def cmd_place(message: Message) -> None:
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Ishlatish: /place 3")
        return
    try:
        p = await get_place(int(parts[1]))
        text = (
            f"🏠 {p['name']}\n"
            f"📍 {p['district_name']} — {p['address']}\n"
            f"🤫 {p['noise_display']} · 📶 {p['wifi_speed']} Mbps · 🔌 {'Bor' if p['socket_count'] else "Yo'q"}\n"
            f"💰 {price_label(p['price_per_hour'])} · 🟢 {p['available_slots']} ta bo'sh\n"
            f"⭐ {float(p['avg_rating']):.1f}" if p.get("avg_rating") else ""
        )
        await message.answer(text.strip())
    except Exception as exc:
        await message.answer(f"Joy topilmadi: {exc}")


# ---------------------------------------------------------------------------
# 🔎 Joy topish (filter flow)
# ---------------------------------------------------------------------------
@dp.message(F.text == "🔎 Joy topish")
async def ask_search(message: Message, state: FSMContext) -> None:
    await state.update_data(search={}, step="search_district")
    await state.set_state(Flow.search_district)
    try:
        districts = await get_districts()
    except Exception as exc:
        logger.warning("districts yuklanmadi: %s", exc)
        districts = []
    buttons = [InlineKeyboardButton(text=d["name"], callback_data=f"val:{d['slug']}") for d in districts]
    rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]
    rows.append([InlineKeyboardButton(text="⏭️ O'tkazib yuborish", callback_data="skip")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await message.answer("1/5 — Tuman tanlang:", reply_markup=kb)


@dp.callback_query(F.data == "skip")
async def on_skip(callback, state: FSMContext) -> None:
    await callback.answer()
    data = await state.get_data()
    step = data.get("step", "search_district")
    await advance(callback.message, state, step, None)


@dp.callback_query(F.data.startswith("val:"))
async def on_value(callback, state: FSMContext) -> None:
    await callback.answer()
    value = callback.data.split(":", 1)[1]
    data = await state.get_data()
    step = data.get("step", "search_district")
    await advance(callback.message, state, step, value)


async def advance(message: Message, state: FSMContext, step: str, value) -> None:
    data = await state.get_data()
    search = data.get("search", {})
    mapping = {
        "search_district": ("district", "search_noise", "2/5 — Shovqin darajasi:", choice_kb(NOISE_CHOICES)),
        "search_noise": ("noise_level", "search_price", "3/5 — Narx:", choice_kb(PRICE_CHOICES)),
        "search_price": ("price", "search_wifi", "4/5 — Wi-Fi tezligi:", choice_kb(WIFI_CHOICES)),
        "search_wifi": ("wifi", "search_socket", "5/5 — Rozetka kerakmi?", choice_kb(YES_NO_CHOICES)),
        "search_socket": ("sockets", "done", None, None),
    }
    key, next_step, prompt, kb = mapping[step]
    if value is not None:
        search[key] = value
    await state.update_data(search=search, step=next_step)
    if next_step == "done":
        await state.clear()
        await run_search(message, search)
    else:
        await message.answer(prompt, reply_markup=kb)


async def run_search(message: Message, filters: dict) -> None:
    await message.answer("🔎 Qidirmoqdaman...")
    params = {"page_size": 5}
    for key in ("district", "noise_level", "price", "wifi", "sockets"):
        if filters.get(key):
            params[key] = filters[key]
    try:
        results = await search_places(params)
        labels = []
        for k, v in filters.items():
            if v:
                labels.append(f"{k}={v}")
        extra = f"Filterlar: {', '.join(labels)}\n\n" if labels else ""
        await send_places(message, results, extra)
    except Exception as exc:
        logger.exception("search failed")
        await message.answer(f"Xatolik yuz berdi: {exc}")


# ---------------------------------------------------------------------------
# 🤖 AI orqali topish
# ---------------------------------------------------------------------------
@dp.message(F.text == "🤖 AI orqali topish")
async def ask_ai(message: Message, state: FSMContext) -> None:
    await state.set_state(Flow.ai_text)
    await message.answer(
        "Talabingizni oddiy tilda yozing, masalan:\n"
        "\"Yunusobodda tinch, bepul va Wi-Fi yaxshi joy kerak.\""
    )


@dp.message(Flow.ai_text)
async def do_ai(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("🤔 AI tahlil qilmoqda...")
    try:
        data = await ai_chat(message.text)
        text = data.get("message", "")
        if len(text) > 3900:
            text = text[:3900] + "..."
        await message.answer(text)
        await send_places(message, [item["place"] for item in data.get("results", [])[:5]])
    except Exception as exc:
        logger.exception("ai failed")
        await message.answer(f"Xatolik yuz berdi: {exc}")


# ---------------------------------------------------------------------------
# 🗺️ Yaqin joylar
# ---------------------------------------------------------------------------
@dp.message(F.text == "🗺️ Yaqin joylar")
async def ask_location(message: Message) -> None:
    await message.answer(
        "📍 Joylashuvingizni yuboring — sizga eng yaqin 5 ta joyni ko'rsataman.",
        reply_markup=LOCATION_KB,
    )


@dp.message(F.location)
async def on_location(message: Message) -> None:
    lat, lng = message.location.latitude, message.location.longitude
    await message.answer("🗺️ Eng yaqin joylarni qidirmoqdaman...", reply_markup=MAIN_KB)
    try:
        results = await nearby_places(lat, lng)
        await send_places(message, results, f"Siz: {lat:.4f}, {lng:.4f}\n\n")
    except Exception as exc:
        logger.exception("nearby failed")
        await message.answer(f"Xatolik yuz berdi: {exc}")


# ---------------------------------------------------------------------------
# ❤️ Sevimlilar
# ---------------------------------------------------------------------------
@dp.message(F.text == "❤️ Sevimlilar")
async def cmd_favorites(message: Message) -> None:
    try:
        data = await get_favorites(str(message.chat.id))
        if not data.get("success"):
            await message.answer(data.get("message", "Xatolik"))
            return
        if not data.get("places"):
            await message.answer("Sevimli joylar bo'sh 😔 Saytda joylarni ❤️ bilan belgilang.")
            return
        await send_places(message, data["places"], f"❤️ {data['user_email']} uchun sevimlilar:\n\n")
    except Exception as exc:
        await message.answer(f"Xatolik yuz berdi: {exc}")


# ---------------------------------------------------------------------------
# 🔔 Bildirishnomalar
# ---------------------------------------------------------------------------
@dp.message(F.text == "🔔 Bildirishnomalar")
async def cmd_notifications(message: Message) -> None:
    try:
        data = await toggle_notifications(str(message.chat.id))
        await message.answer(data.get("message", "Xatolik yuz berdi"))
    except Exception as exc:
        await message.answer(f"Xatolik yuz berdi: {exc}")


# ---------------------------------------------------------------------------
# 🔗 Hisobni bog'lash
# ---------------------------------------------------------------------------
@dp.message(F.text == "🔗 Hisobni bog'lash")
async def ask_link(message: Message, state: FSMContext) -> None:
    await state.set_state(Flow.link_code)
    await message.answer(
        "1. quietspace saytida profil sahifasiga kiring.\n"
        "2. «Telegram bilan bog'lash» tugmasini bosing — kod olasiz.\n"
        "3. Shu kodni menga yuboring (yoki /link <kod>)."
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