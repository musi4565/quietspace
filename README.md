# QuietSpace Tashkent 🌿

Shahardagi jimjit, Wi-Fi va rozetkasi bor qulay joylarni topish platformasi — **Hackathon demo**.

## Texnologiyalar

- **Backend** — Django 5 + Django REST Framework + PostgreSQL (JWT auth, AI matching, Telegram linking)
- **Frontend** — React 18 + Vite + React Router + Axios + Leaflet (xarita)
- **Bot** — Telegram bot (Aiogram 3) — qidiruv, AI topish, hisobni bog'lash
- **AI Assistant** — OpenAI-compatible API (`AI_API_KEY` bo'lmasa offline rule-based rejim ishlaydi)

## Loyiha tuzilishi

```
quietspace/
    backend/      # Django REST API (port 8000)
    frontend/     # React + Vite (port 5173)
    bot/          # Telegram bot (Aiogram 3)
    .env          # Maxfiy sozlamalar (GitHub'ga chiqmaydi)
    .env.example  # Sozlamalar namunasi
```

## O'rnatish

1. Repositoriyani klonlash va virtual environment:

   ```bash
   git clone https://github.com/musi4565/quietspace.git
   cd quietspace
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   source .venv/bin/activate     # Linux/Mac
   ```

2. Backend:

   ```bash
   cp .env.example .env          # so'ng haqiqiy qiymatlarni kiriting
   pip install -r backend/requirements.txt
   cd backend
   python manage.py migrate
   python manage.py seed_places  # 12 demo joy
   python manage.py runserver 127.0.0.1:8000
   ```

3. Frontend:

   ```bash
   cd frontend
   npm install
   npm run dev                   # http://localhost:5173
   ```

4. Telegram bot:

   ```bash
   cd bot
   pip install -r bot/requirements.txt
   python main.py                # .env da TELEGRAM_BOT_TOKEN bo'lishi kerak
   ```

## Asosiy funksiyalar

- 🔎 Joylarni qidirish/filter — tuman, shovqin, narx, Wi-Fi tezligi, bo'sh joylar
- 🗺️ Xarita — barcha joylar Leaflet xaritasida
- 🤖 AI Assistant — "Chilonzorda tinch, rozetkasi bor joy qani?" → eng mos joylar + moslik %
- ❤️ Sevimlilar, ⭐ sharhlar va reytinglar
- 🔗 Telegram bilan bog'lanish — sayt hisobi ↔ bot chat (`/link <kod>`)
- 📊 Admin panel — `/api/panel/` dashboard, joylarni tasdiqlash

## API qisqacha

| Endpoint | Tavsif |
|---|---|
| `POST /api/auth/register/`, `login/` | Ro'yxatdan o'tish / kirish (JWT) |
| `GET /api/places/` | Joylar (search, district, noise_level, price, wifi, available) |
| `GET /api/places/<id>/` | Joy detali |
| `POST /api/ai/chat/` | AI talab → mos joylar + match % |
| `POST /api/telegram/link/confirm/` | Bot kod orqali hisobni bog'laydi |
| `GET /api/panel/dashboard/` | Admin statistikasi |

## Demo akkauntlar

- Admin: `admin@quietspace.uz` / `2thqdj0rzxn5vb`
- Owner: `owner@quietspace.uz` / `ownerpass123`
- User: `test@test.uz` / `StrongPass123`

## Testlar

```bash
cd backend
python manage.py test      # 71 test
```

## Git workflow

Har bir tugallangan o'zgarishdan keyin: `git status` → secret scan (`git diff --cached`) → commit → push. `.env` hech qachon push qilinmaydi.