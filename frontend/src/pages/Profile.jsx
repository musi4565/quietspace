import { useEffect, useState } from "react";
import api, { errorMessage } from "../api";
import { useAuth } from "../context/AuthContext";

export default function Profile() {
  const { user, setUser } = useAuth();
  const [form, setForm] = useState({ full_name: "", current_password: "", new_password: "" });
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (user) setForm((f) => ({ ...f, full_name: user.full_name }));
  }, [user]);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setMsg("");
    setError("");
    try {
      const { data } = await api.post("/auth/me/", {
        full_name: form.full_name,
        current_password: form.current_password,
        new_password: form.new_password || null,
      });
      setUser(data.user);
      setForm((f) => ({ ...f, current_password: "", new_password: "" }));
      setMsg("Profil yangilandi");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="page">
      <h1>👤 Profil</h1>
      <form className="card auth-card" onSubmit={submit}>
        <input
          className="input"
          placeholder="Ism va familiya"
          value={form.full_name}
          onChange={(e) => setForm({ ...form, full_name: e.target.value })}
          required
        />
        <input className="input" value={user?.email ?? ""} disabled />
        <input
          className="input"
          type="password"
          placeholder="Joriy parol (o'zgartirish uchun)"
          value={form.current_password}
          onChange={(e) => setForm({ ...form, current_password: e.target.value })}
        />
        <input
          className="input"
          type="password"
          placeholder="Yangi parol"
          minLength={8}
          value={form.new_password}
          onChange={(e) => setForm({ ...form, new_password: e.target.value })}
        />
        {msg && <p className="msg">{msg}</p>}
        {error && <p className="error-text">{error}</p>}
        <button className="btn btn-primary" disabled={busy}>
          {busy ? "Saqlanmoqda..." : "Saqlash"}
        </button>
      </form>
    </div>
  );
}