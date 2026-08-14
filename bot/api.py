import httpx

try:
    from bot.config import BACKEND_URL
except ImportError:  # standalone rejim (python main.py)
    from config import BACKEND_URL


async def _get(path: str, params: dict = None) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(f"{BACKEND_URL}{path}", params=params or {})
        resp.raise_for_status()
        return resp.json()


async def _post(path: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{BACKEND_URL}{path}", json=payload)
        if resp.status_code < 300:
            return resp.json()
        try:
            return {"success": False, "message": resp.json().get("message", "Xatolik")}
        except ValueError:
            return {"success": False, "message": f"Xatolik (HTTP {resp.status_code})"}


async def get_districts() -> list:
    return await _get("/api/places/districts/")


async def search_places(params: dict) -> list:
    data = await _get("/api/places/", params=params)
    return data.get("results", [])


async def get_place(place_id: int) -> dict:
    return await _get(f"/api/places/{place_id}/")


async def nearby_places(lat: float, lng: float) -> list:
    return await search_places({"lat": lat, "lng": lng, "page_size": 5})


async def ai_chat(message: str) -> dict:
    return await _post("/api/ai/chat/", {"message": message})


async def confirm_link(code: str, chat_id: str, username: str = "") -> dict:
    return await _post(
        "/api/telegram/link/confirm/",
        {"code": code, "chat_id": str(chat_id), "username": username},
    )


async def get_favorites(chat_id: str) -> dict:
    return await _get("/api/telegram/favorites/", {"chat_id": chat_id})


async def toggle_notifications(chat_id: str) -> dict:
    return await _post("/api/telegram/notifications/", {"chat_id": str(chat_id)})