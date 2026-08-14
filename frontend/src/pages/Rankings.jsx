import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import { priceLabel } from "../components/PlaceCard";

export default function Rankings() {
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/rankings/")
      .then(({ data }) => setCategories(data.categories))
      .catch(() => setError("Reytinglar yuklanmadi"));
  }, []);

  if (error) return <div className="page"><p className="error-text">{error}</p></div>;

  return (
    <div className="page">
      <h1>🏆 Reytinglar</h1>
      {categories.map((cat) => (
        <section key={cat.category}>
          <h2>{cat.title}</h2>
          <div className="rank-list">
            {cat.places.map((p, i) => (
              <Link key={p.id} to={`/places/${p.id}`} className="rank-row">
                <span className="rank-num">{i + 1}</span>
                <span className="rank-name">{p.name}</span>
                <span className="muted">📍 {p.district_name}</span>
                <span className="rank-value">
                  {cat.category === "best" && p.ranking_value != null
                    ? `⭐ ${Number(p.ranking_value).toFixed(1)}`
                    : cat.category === "wifi"
                      ? `📶 ${p.ranking_value} Mbps`
                      : priceLabel(p.price_per_hour)}
                </span>
              </Link>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}