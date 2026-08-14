import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const links = [
    { to: "/", label: "🏠 Bosh sahifa" },
    { to: "/places", label: "🔎 Joylar" },
    { to: "/map", label: "🗺️ Xarita" },
    { to: "/ai", label: "🤖 AI Assistant" },
    { to: "/rankings", label: "🏆 Reyting" },
    ...(user ? [{ to: "/favorites", label: "❤️ Sevimlilar" }] : []),
    ...(user ? [{ to: "/profile", label: "👤 Profil" }] : []),
  ];

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="brand">
          🌿 QuietSpace <span>Tashkent</span>
        </Link>
        <button className="burger" onClick={() => setOpen(!open)} aria-label="Menu">
          ☰
        </button>
        <div className={`nav-links ${open ? "open" : ""}`}>
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
              onClick={() => setOpen(false)}
            >
              {l.label}
            </NavLink>
          ))}
          <div className="nav-auth">
            {user ? (
              <button
                className="btn btn-outline btn-sm"
                onClick={() => {
                  logout();
                  navigate("/");
                }}
              >
                Chiqish
              </button>
            ) : (
              <>
                <Link to="/login" className="btn btn-outline btn-sm" onClick={() => setOpen(false)}>
                  Kirish
                </Link>
                <Link to="/register" className="btn btn-primary btn-sm" onClick={() => setOpen(false)}>
                  Ro'yxatdan o'tish
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}