import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { errorMessage } from "../api";
import { priceLabel, slotsLabel } from "../components/PlaceCard";

export default function Favorites() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    api
      .get("/favorites/")
      .then(({ data }) => setItems(data.results ?? data))
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const remove = async (placeId) => {
    try {
      await api.delete(`/favorites/remove/${placeId}/`);
      load();
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  if (loading) return <div className="loading">Yuklanmoqda...</div>;

  return (
    <div className="page">
      <h1>❤️ Sevimli joylar</h1>
      {error && <p className="error-text">{error}</p>}
      {items.length === 0 && (
        <div className="empty">
          <p>Hali sevimlilar yo'q</p>
          <Link to="/places" className="btn btn-primary">
            Joylarni ko'rish
          </Link>
        </div>
      )}
      <div className="list">
        {items.map((f) => (
          <div key={f.id} className="card row-card">
            <div>
              <Link to={`/places/${f.place.id}`} className="place-card-name">
                {f.place.name}
              </Link>
              <p className="muted">
                📍 {f.place.district_name} · 🤫 {f.place.noise_display} · 📶 {f.place.wifi_speed} Mbps
              </p>
              <p>
                💰 {priceLabel(f.place.price_per_hour)} ·{" "}
                <span className={f.place.available_slots > 0 ? "slots-ok" : "slots-full"}>
                  {slotsLabel(f.place.available_slots)}
                </span>
              </p>
            </div>
            <button className="btn btn-outline btn-sm" onClick={() => remove(f.place.id)}>
              Olib tashlash
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}