import { useEffect, useState } from "react";
import api from "../api";
import PlaceCard from "../components/PlaceCard";
import { errorMessage } from "../api";

const NOISE_OPTIONS = [
  { value: "", label: "Har qanday shovqin" },
  { value: "very_quiet", label: "🤫 Juda tinch" },
  { value: "quiet", label: "🙂 Tinch" },
  { value: "average", label: "😐 O'rtacha" },
  { value: "noisy", label: "📣 Shovqinli" },
];

export default function Places() {
  const [places, setPlaces] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [favIds, setFavIds] = useState(new Set());
  const [filters, setFilters] = useState({ district: "", noise_level: "", price: "", wifi: "" });
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/places/districts/").then(({ data }) => setDistricts(data)).catch(() => {});
    api.get("/favorites/ids/").then(({ data }) => setFavIds(new Set(data.place_ids))).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    api
      .get("/places/", {
        params: {
          ...filters,
          search: search || undefined,
          page,
          page_size: 12,
        },
      })
      .then(({ data }) => {
        setPlaces((prev) => (page === 1 ? data.results : [...prev, ...data.results]));
        setHasMore(!!data.next);
      })
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, [filters, search, page]);

  const applyFilter = (key, value) => {
    setPage(1);
    setFilters((f) => ({ ...f, [key]: value }));
  };

  return (
    <div className="page">
      <div className="section-head">
        <h1>🔎 Joylar</h1>
      </div>

      <div className="filters">
        <input
          className="input"
          placeholder="Qidirish: nom, manzil..."
          value={search}
          onChange={(e) => {
            setPage(1);
            setSearch(e.target.value);
          }}
        />
        <select
          className="input"
          value={filters.district}
          onChange={(e) => applyFilter("district", e.target.value)}
        >
          <option value="">Barcha tumanlar</option>
          {districts.map((d) => (
            <option key={d.id} value={d.slug}>
              {d.name}
            </option>
          ))}
        </select>
        <select
          className="input"
          value={filters.noise_level}
          onChange={(e) => applyFilter("noise_level", e.target.value)}
        >
          {NOISE_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <select className="input" value={filters.price} onChange={(e) => applyFilter("price", e.target.value)}>
          <option value="">Narxi</option>
          <option value="free">Bepul</option>
          <option value="under_50k">50 mingdan kam</option>
          <option value="50k_100k">50–100 ming</option>
          <option value="over_100k">100 mingdan yuqori</option>
        </select>
        <select className="input" value={filters.wifi} onChange={(e) => applyFilter("wifi", e.target.value)}>
          <option value="">Wi-Fi tezligi</option>
          <option value="above_50">50+ Mbps</option>
          <option value="above_100">100+ Mbps</option>
        </select>
      </div>

      {error && <p className="error-text">{error}</p>}
      {loading && <p className="loading">Yuklanmoqda...</p>}

      {!loading && places.length === 0 && (
        <div className="empty">
          <p>Hech narsa topilmadi 😔</p>
          <p className="muted">Filterlarni o'zgartirib ko'ring yoki AI assistentdan so'rang.</p>
        </div>
      )}

      <div className="grid">
        {places.map((p) => (
          <PlaceCard key={p.id} place={p} favIds={favIds} />
        ))}
      </div>

      {hasMore && (
        <div className="center">
          <button className="btn btn-outline" onClick={() => setPage((p) => p + 1)}>
            Ko'proq yuklash
          </button>
        </div>
      )}
    </div>
  );
}