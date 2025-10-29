// feat(auth): login form, minimal UI following existing theme
// feat(ui): add sticky header with Login button and polish spacing
import { useEffect, useState } from "react";
import { useAuth } from "../auth";

export default function Login() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    const ok = await login(email, password);
    setLoading(false);
    if (!ok) setError("Invalid credentials");
  }

  useEffect(() => {
    setError("");
  }, [email, password]);

  return (
    <>
      <header className="topbar sticky" aria-label="Login header">
        <div className="brand"><strong>Legacy Skye</strong> <span className="muted">Steward</span></div>
        <div className="header-controls" style={{ display:'flex', alignItems:'center', gap:10 }}>
          <button className="primary" onClick={() => { if (!loading) void login(email, password); }} aria-label="Login" disabled={loading}>
            {loading ? "Signing in..." : "Login"}
          </button>
        </div>
      </header>
      <div className="container" style={{ display: "grid", placeItems: "center", minHeight: "80vh" }}>
      <form className="card" style={{ maxWidth: 420, width: "100%" }} onSubmit={onSubmit} aria-label="Login form">
        <h3>Sign in</h3>
        <div className="muted">Use your email and password.</div>
        <div style={{ display: "grid", gap: 8, marginTop: 10 }}>
          <input type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required />
          <input type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} required />
          {error && <div className="muted" role="alert" style={{ color: "#ef4444" }}>{error}</div>}
          <button className="primary" disabled={loading} aria-label="Sign in">{loading ? "Signing in..." : "Sign in"}</button>
        </div>
      </form>
      </div>
    </>
  );
}
