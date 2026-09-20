import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { user, login, error, loading } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  if (user) return <Navigate to="/dashboard" replace />;

  const handleSubmit = async (e) => {
    e.preventDefault();
    const ok = await login(username, password);
    if (ok) navigate("/dashboard");
  };

  return (
    <div className="login-shell">
      <div className="login-hero">
        <h1>Every record, every request, one place.</h1>
        <p>
          Manage employee profiles, daily attendance, and leave approvals through a single,
          role-aware workspace built for HR teams and the people they support.
        </p>
      </div>

      <div className="login-form-side">
        <div className="login-box">
          <h2>Sign in</h2>
          <p style={{ color: "var(--ink-soft)", marginTop: 0 }}>Use your work account to continue.</p>

          {error && <div className="alert alert-error">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                required
              />
            </div>
            <div className="field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
            </div>
            <button className="btn btn-accent" type="submit" disabled={loading} style={{ width: "100%", justifyContent: "center" }}>
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </form>

          <div className="demo-creds">
            Demo accounts (after running <code>seed_demo_data</code>):
            <br />
            Admin — <code>admin / ######</code>
            <br />
            HR — <code>hr_manager / HrPass123!</code>
            <br />
            Employee — <code>jdoe / EmployeePass123!</code>
          </div>
        </div>
      </div>
    </div>
  );
}
