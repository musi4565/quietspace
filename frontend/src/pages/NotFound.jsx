import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="page center">
      <h1>404</h1>
      <p className="muted">Bunday sahifa topilmadi</p>
      <Link to="/" className="btn btn-primary">
        Bosh sahifa
      </Link>
    </div>
  );
}