# QuietSpace

QuietSpace - tinch joylar va xizmatlar topishga yordam beruvchi platforma. (To'liq tavsif loyiha talablariga qarab keyinroq kengaytiriladi.)

## Loyiha tuzilishi

```
quietspace/
    frontend/     # Frontend (kelajakda)
    backend/      # Backend (kelajakda)
    bot/          # Telegram bot (kelajakda)
    .env          # Maxfiy sozlamalar (GitHub'ga chiqmaydi)
    .env.example  # Sozlamalar namunasi (placeholder qiymatlar)
    .gitignore
    README.md
```

## O'rnatish

1. Repositoriyani klonlash:
   ```bash
   git clone https://github.com/musi4565/quietspace.git
   cd quietspace
   ```

2. Virtual environment yaratish (Python loyihasi uchun):
   ```bash
   python -m venv .venv
   ```

3. Bog'liqliklarni o'rnatish (texnologiyaga qarab keyinroq to'ldiriladi).

## .env sozlash

```bash
cp .env.example .env
```

So'ng `.env` faylini ochib, haqiqiy qiymatlarni kiriting (SECRET_KEY, DATABASE_*, TELEGRAM_BOT_TOKEN, AI_API_KEY, JWT_SECRET).

**MUHIM:** `.env` fayli hech qachon GitHub'ga push qilinmasligi kerak - u `.gitignore` da allaqachon qo'shilgan.

## Ishga tushirish

(Texnologiya stack aniqlangandan keyin to'ldiriladi.)

## Git workflow

Har bir tugallangan o'zgarishdan keyin:

```bash
git status          # o'zgarishlarni tekshirish
git diff --cached   # staged fayllarni tekshirish (secret scan)
git add <fayllar>   # faqat kerakli fayllarni stage qilish
git commit -m "feat: ..."  # mazmunli commit xabari
git push            # GitHub'ga push
```

Qoidalar:

- Commitdan oldin **har doim** secret scan qilinadi (.env, token, password, key).
- `git add .` ko'r-ko'rona ishlatilmaydi.
- Test muvaffaqiyatsiz bo'lsa - commit/push qilinmaydi.
- Git tarix qayta yozilmaydi, force push ishlatilmaydi.