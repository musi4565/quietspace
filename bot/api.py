import httpx

from config import BACKEND_URL


async def search_places(text: str) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{BACKEND_URL}/api/places/", params={"search": text, "page_size": 5})
        resp.raise_for_status()
        return resp.json()


async def ai_chat(message: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{BACKEND_URL}/api/ai/chat/", json={"message": message})
        resp.raise_for_status()
        return resp.json()


async def confirm_link(code: str, chat_id: str, username: str = "") -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{BACKEND_URL}/api/telegram/link/confirm/",
            json={"code": code, "chat_id": str(chat_id), "username": username},
        )
        return resp.json() if resp.status_code < 300 else {"success": False, "message": resp.json().get("message", "Xatolik")}