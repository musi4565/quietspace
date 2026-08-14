import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import api, { errorMessage } from "../api";
import { priceLabel, slotsLabel } from "../components/PlaceCard";

const EXAMPLES = [
  "Chilonzorda tinch, rozetkasi bor joy qani?",
  "Shayxontohurda bepul, yaxshi Wi-Fi joy top",
  "Yunusobodda shovqinli bo'lmagan, 50 mingdan kam joy",
];

export default function AIChat() {
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "Salom! 👋 Menga talabingizni yozing — masalan: \"Chilonzorda rozetkasi bor, tinch joy qani?\" Men eng mos joylarni topaman.",
    },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [results, setResults] = useState({});
  const [source, setSource] = useState(null);
  const endRef = useRef(null);

  useEffect(() => {
    api
      .get("/ai/status/")
      .then(({ data }) => setSource(data.source))
      .catch(() => {});
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text) => {
    const message = (text ?? input).trim();
    if (!message || busy) return;
    setInput("");
    setBusy(true);
    setMessages((m) => [...m, { role: "user", text: message }]);
    try {
      const { data } = await api.post("/ai/chat/", { message });
      setMessages((m) => [...m, { role: "bot", text: data.message }]);
      setResults((r) => ({ ...r, [message]: data.results ?? [] }));
    } catch (err) {
      setMessages((m) => [...m, { role: "bot", text: errorMessage(err) }]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="page">
      <h1>🤖 AI Assistant</h1>
      <p className="muted">
        {source === "ai"
          ? "OpenAI bilan ishlayapti — eng mos joylarni topadi."
          : "Hozircha mahalliy (offline) rejim — AI kalitsiz ham ishlaydi, talablarni tahlil qiladi va eng mos joylarni topadi."}
      </p>

      <div className="chat">
        {messages.map((m, i) => (
          <div key={i} className={`chat-msg ${m.role}`}>
            <div className="bubble">{m.text}</div>
            {m.role === "bot" && results[m.text]?.length > 0 && (
              <div className="chat-results">
                {results[m.text].map((r) => (
                  <Link key={r.place.id} to={`/places/${r.place.id}`} className="chat-result">
                    <div>
                      <strong>{r.place.name}</strong>
                      <span className="muted">
                        📍 {r.place.district_name} · 🤫 {r.place.noise_display}
                      </span>
                    </div>
                    <div className="match">
                      <span className="match-bar">
                        <span style={{ width: `${r.match_percent}%` }} />
                      </span>
                      <span className="match-pct">{r.match_percent}%</span>
                    </div>
                    <div className="muted small">
                      💰 {priceLabel(r.place.price_per_hour)} · {slotsLabel(r.place.available_slots)}
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        ))}
        {busy && <div className="chat-msg bot"><div className="bubble typing">Yozmoqda...</div></div>}
        <div ref={endRef} />
      </div>

      <div className="examples">
        {EXAMPLES.map((ex) => (
          <button key={ex} className="chip" onClick={() => send(ex)} disabled={busy}>
            {ex}
          </button>
        ))}
      </div>

      <form
        className="chat-input"
        onSubmit={(e) => {
          e.preventDefault();
          send();
        }}
      >
        <input
          className="input"
          placeholder="Talabingizni yozing..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button className="btn btn-primary" disabled={busy || !input.trim()}>
          Yuborish
        </button>
      </form>
    </div>
  );
}