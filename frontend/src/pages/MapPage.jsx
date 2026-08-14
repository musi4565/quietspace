import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { Link } from "react-router-dom";
import api from "../api";
import { priceLabel, slotsLabel } from "../components/PlaceCard";

const icon = L.divIcon({
  className: "custom-marker",
  html: "🌿",
  iconSize: [30, 30],
  iconAnchor: [15, 30],
});

export default function MapPage() {
  const [places, setPlaces] = useState([]);
  const [error, setError] = useState("");
  const [center] = useState([41.2995, 69.2401]);

  useEffect(() => {
    api
      .get("/places/", { params: { page_size: 100 } })
      .then(({ data }) => setPlaces(data.results.filter((p) => p.latitude && p.longitude)))
      .catch(() => setError("Xarita yuklanmadi"));
  }, []);

  return (
    <div className="page map-page">
      <h1>🗺️ Xarita</h1>
      {error && <p className="error-text">{error}</p>}
      <div className="map-wrap">
        <MapContainer center={center} zoom={12} style={{ height: "100%", width: "100%" }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {places.map((p) => (
            <Marker key={p.id} position={[p.latitude, p.longitude]} icon={icon}>
              <Popup>
                <strong>{p.name}</strong>
                <br />
                <span className="muted">📍 {p.district_name}</span>
                <br />
                {p.avg_rating ? <span>⭐ {p.avg_rating.toFixed(1)} · </span> : null}
                💰 {priceLabel(p.price_per_hour)}
                <br />
                <span className={p.available_slots > 0 ? "slots-ok" : "slots-full"}>
                  {slotsLabel(p.available_slots)}
                </span>
                <br />
                <Link to={`/places/${p.id}`}>Batafsil →</Link>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}