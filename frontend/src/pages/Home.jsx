import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import PlaceCard from "../components/PlaceCard";

export default function Home() {
  const [places, setPlaces] = useState([]);
  const [favIds, setFavIds] = useState(new Set());
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/places/", { params: { page_size: 6 } })
      .then(({ data }) => setPlaces(data.results))
      .catch(() => setError("Joylar yuklanmadi"));
    api
      .get("/favorites/ids/")
      .then(({ data }) => setFavIds(new Set(data.place_ids)))
      .catch(() => {});
  }, []);

  return (
    <div className="page">
      <section className="hero">
        <h1>🌿 QuietSpace Tashkent</h1>
        <p>
          Shahardagi jimjit, Wi-Fi va rozetkasi bor joylarni toping — bir soatlik, dam olishsiz va
          qulay ish muhiti.
        </p>
        <div className="hero-actions">
          <Link to="/places" className="btn btn-primary btn-lg">
            🔎 Joylarni qidirish
          </Link>
          <Link to="/ai" className="btn btn-outline btn-lg">
            🤖 AI bilan topish
          </Link>
        </div>
      </section>

      {error && <p className="error-text">{error}</p>}

      <section>
        <div className="section-head">
          <h2>Eng zo'r joylar</h2>
          <Link to="/places" className="btn btn-outline btn-sm">
            Hammasi →
          </Link>
        </div>
        <div className="grid">
          {places.map((p) => (
            <PlaceCard key={p.id} place={p} favIds={favIds} />
          ))}
        </div>
      </section>

      <section className="features">
        <div className="feature">
          <span className="feature-icon">🤫</span>
          <h3>Shovqin darajasi</h3>
          <p>Har bir joy bo'yicha real shovqin bahosi — jimjit joylarni osongina toping.</p>
        </div>
        <div className="feature">
          <span className="feature-icon">🤖</span>
          <h3>AI Assistant</h3>
          <p>"Chilonzorda rozetkasi bor, tinch joy qani?" deb yozing — AI sizga eng mosini topadi.</p>
        </div>
        <div className="feature">
          <span className="feature-icon">🗺️</span>
          <h3>Xarita</h3>
          <p>Barcha joylar Toshkent xaritasida — yaqinidagi qulay joyni bir ko'rishda aniqlang.</p>
        </div>
      </section>
    </div>
  );
}