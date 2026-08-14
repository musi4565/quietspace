import { useState } from "react";
import { Link } from "react-router-dom";
import api, { errorMessage } from "../api";
import { useAuth } from "../context/AuthContext";

export function priceLabel(price) {
  if (price === 0) return "Bepul";
  return `${price.toLocaleString("uz-UZ")} so'm`;
}

export function slotsLabel(slots) {
  if (slots === 0) return "🔴 Joy qolmagan";
  if (slots < 5) return `🟡 ${slots} ta bo'sh`;
  return `🟢 ${slots} ta bo'sh`;
}

export default function PlaceCard({ place, favIds = new Set() }) {
  const { user } = useAuth();
  const [fav, setFav] = useState(favIds.has(place.id));
  const [msg, setMsg] = useState("");

  const toggleFavorite = async (e) => {
    e.preventDefault();
    if (!user) {
      setMsg("Sevimli uchun tizimga kiring");
      return;
    }
    try {
      if (fav) {
        await api.delete(`/favorites/remove/${place.id}/`);
        setFav(false);
      } else {
        await api.post("/favorites/add/", { place: place.id });
        setFav(true);
      }
    } catch (err) {
      setMsg(errorMessage(err));
    }
  };

  return (
    <div className="place-card">
      <Link to={`/places/${place.id}`} className="place-card-img-wrap">
        {place.image ? (
          <img src={place.image} alt={place.name} className="place-card-img" />
        ) : (
          <div className="place-card-img placeholder">🌿</div>
        )}
        <span className="badge-rating">⭐ {place.avg_rating ? place.avg_rating.toFixed(1) : "—"}</span>
      </Link>
      <div className="place-card-body">
        <div className="place-card-top">
          <Link to={`/places/${place.id}`} className="place-card-name">
            {place.name}
          </Link>
          <button className={`heart ${fav ? "active" : ""}`} onClick={toggleFavorite} aria-label="Sevimli">
            {fav ? "❤️" : "🤍"}
          </button>
        </div>
        <div className="place-card-meta">
          <span>📍 {place.district_name}</span>
          <span>🤫 {place.noise_display}</span>
          <span>📶 {place.wifi_speed} Mbps</span>
          <span>🔌 {place.socket_count > 0 ? "Bor" : "Yo'q"}</span>
          <span className={place.available_slots > 0 ? "slots-ok" : "slots-full"}>
            {slotsLabel(place.available_slots)}
          </span>
          <span className="price">💰 {priceLabel(place.price_per_hour)}</span>
        </div>
        {msg && <p className="error-text">{msg}</p>}
        <Link to={`/places/${place.id}`} className="btn btn-outline btn-sm btn-block">
          Batafsil
        </Link>
      </div>
    </div>
  );
}