import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Link } from "react-router-dom";
import api, { errorMessage } from "../api";
import { priceLabel, slotsLabel } from "../components/PlaceCard";
import { useAuth } from "../context/AuthContext";

export default function PlaceDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [place, setPlace] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [fav, setFav] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ rating: 5, comment: "" });
  const [msg, setMsg] = useState("");

  useEffect(() => {
    setLoading(true);
    Promise.all([api.get(`/places/${id}/`), api.get(`/reviews/place/${id}/`)])
      .then(([p, r]) => {
        setPlace(p.data);
        setReviews(r.data.results ?? r.data);
      })
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
    if (user) {
      api
        .get(`/favorites/status/${id}/`)
        .then(({ data }) => setFav(data.is_favorite))
        .catch(() => {});
    }
  }, [id, user]);

  const toggleFavorite = async () => {
    if (!user) {
      setMsg("Sevimli uchun tizimga kiring");
      return;
    }
    try {
      if (fav) {
        await api.delete(`/favorites/remove/${id}/`);
        setFav(false);
      } else {
        await api.post("/favorites/add/", { place: id });
        setFav(true);
      }
      setMsg("");
    } catch (err) {
      setMsg(errorMessage(err));
    }
  };

  const submitReview = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/reviews/place/${id}/create/`, { rating: form.rating, comment: form.comment });
      const r = await api.get(`/reviews/place/${id}/`);
      setReviews(r.data.results ?? r.data);
      setForm({ rating: 5, comment: "" });
      setMsg("Sharh qo'shildi");
    } catch (err) {
      setMsg(errorMessage(err));
    }
  };

  if (loading) return <div className="loading">Yuklanmoqda...</div>;
  if (error || !place)
    return (
      <div className="page">
        <p className="error-text">{error || "Joy topilmadi"}</p>
        <Link to="/places" className="btn btn-outline">
          ← Joylarga qaytish
        </Link>
      </div>
    );

  return (
    <div className="page">
      <div className="detail">
        <div className="detail-img-wrap">
          {place.image ? (
            <img src={place.image} alt={place.name} className="detail-img" />
          ) : (
            <div className="detail-img placeholder">🌿</div>
          )}
        </div>
        <div className="detail-body">
          <div className="detail-top">
            <div>
              <h1>{place.name}</h1>
              <p className="muted">
                📍 {place.district_name} — {place.address}
              </p>
            </div>
            <button className={`heart big ${fav ? "active" : ""}`} onClick={toggleFavorite}>
              {fav ? "❤️" : "🤍"}
            </button>
          </div>

          <div className="detail-stats">
            <div className="stat">
              <span className="stat-value">⭐ {place.avg_rating ? place.avg_rating.toFixed(1) : "—"}</span>
              <span className="stat-label">Baholash</span>
            </div>
            <div className="stat">
              <span className="stat-value">🤫 {place.noise_display}</span>
              <span className="stat-label">Shovqin</span>
            </div>
            <div className="stat">
              <span className="stat-value">📶 {place.wifi_speed} Mbps</span>
              <span className="stat-label">Wi-Fi</span>
            </div>
            <div className="stat">
              <span className="stat-value">🔌 {place.socket_count > 0 ? "Bor" : "Yo'q"}</span>
              <span className="stat-label">Rozetka</span>
            </div>
            <div className="stat">
              <span className="stat-value">💰 {priceLabel(place.price_per_hour)}</span>
              <span className="stat-label">Soatiga</span>
            </div>
            <div className="stat">
              <span className={`stat-value ${place.available_slots > 0 ? "slots-ok" : "slots-full"}`}>
                {slotsLabel(place.available_slots)}
              </span>
              <span className="stat-label">O'rindiq {place.capacity} ta</span>
            </div>
            {place.open_time && (
              <div className="stat">
                <span className="stat-value">🕐 {place.open_time.slice(0, 5)}–{place.close_time.slice(0, 5)}</span>
                <span className="stat-label">Ish vaqti</span>
              </div>
            )}
          </div>

          {place.description && <p className="desc">{place.description}</p>}

          {place.latitude && place.longitude && (
            <a
              className="btn btn-outline btn-sm"
              href={`https://www.google.com/maps?q=${place.latitude},${place.longitude}`}
              target="_blank"
              rel="noreferrer"
            >
              🗺️ Xaritada ochish
            </a>
          )}
        </div>
      </div>

      {msg && <p className="msg">{msg}</p>}

      <section>
        <h2>Sharhlar ({reviews.length})</h2>
        <div className="reviews">
          {reviews.length === 0 && <p className="muted">Hali sharh yo'q — birinchi bo'ling!</p>}
          {reviews.map((r) => (
            <div key={r.id} className="review">
              <div className="review-top">
                <strong>{r.user_name}</strong>
                <span>{"⭐".repeat(r.rating)}</span>
              </div>
              {r.comment && <p>{r.comment}</p>}
              <span className="muted small">{new Date(r.created_at).toLocaleDateString("uz-UZ")}</span>
            </div>
          ))}
        </div>
      </section>

      {user && (
        <section>
          <h2>Sharh qoldirish</h2>
          <form className="review-form" onSubmit={submitReview}>
            <select
              className="input"
              value={form.rating}
              onChange={(e) => setForm({ ...form, rating: Number(e.target.value) })}
            >
              {[5, 4, 3, 2, 1].map((n) => (
                <option key={n} value={n}>
                  {"⭐".repeat(n)}
                </option>
              ))}
            </select>
            <textarea
              className="input"
              placeholder="Fikringiz..."
              value={form.comment}
              onChange={(e) => setForm({ ...form, comment: e.target.value })}
              rows={3}
            />
            <button className="btn btn-primary">Yuborish</button>
          </form>
        </section>
      )}
    </div>
  );
}