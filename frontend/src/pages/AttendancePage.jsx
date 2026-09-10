import { useEffect, useState, useCallback } from "react";
import Layout from "../components/Layout";
import StatusBadge from "../components/StatusBadge";
import { useAuth } from "../context/AuthContext";
import { attendanceApi } from "../api/resources";

export default function AttendancePage() {
  const { isAdminOrHR } = useAuth();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dateFilter, setDateFilter] = useState("");
  const [actionMessage, setActionMessage] = useState("");
  const [actionError, setActionError] = useState("");

  const load = useCallback(async (date = "") => {
    setLoading(true);
    try {
      const params = date ? { date } : {};
      const { data } = isAdminOrHR
        ? await attendanceApi.list(params)
        : await attendanceApi.myHistory(params);
      setRecords(data.results || data);
    } finally {
      setLoading(false);
    }
  }, [isAdminOrHR]);

  useEffect(() => {
    load();
  }, [load]);

  const today = new Date().toISOString().slice(0, 10);
  const todayRecord = records.find((r) => r.date === today);

  const handleCheckIn = async () => {
    setActionError("");
    try {
      await attendanceApi.checkIn();
      setActionMessage("Checked in — have a great day.");
      load(dateFilter);
    } catch (err) {
      setActionError(err.response?.data?.detail || "Couldn't check in.");
    }
  };

  const handleCheckOut = async () => {
    setActionError("");
    try {
      await attendanceApi.checkOut();
      setActionMessage("Checked out — see you tomorrow.");
      load(dateFilter);
    } catch (err) {
      setActionError(err.response?.data?.detail || "Couldn't check out.");
    }
  };

  const handleFilter = (e) => {
    e.preventDefault();
    load(dateFilter);
  };

  return (
    <Layout>
      <div className="page-header">
        <div>
          <h1>Attendance</h1>
          <p>
            {isAdminOrHR
              ? "Daily check-in and check-out records across the organization."
              : "Track your own daily check-in and check-out times."}
          </p>
        </div>
        {!isAdminOrHR && (
          <div style={{ display: "flex", gap: "0.6rem" }}>
            <button className="btn btn-accent" onClick={handleCheckIn} disabled={!!todayRecord?.check_in}>
              Check in
            </button>
            <button className="btn btn-outline" onClick={handleCheckOut} disabled={!todayRecord?.check_in || !!todayRecord?.check_out}>
              Check out
            </button>
          </div>
        )}
      </div>

      {actionMessage && <div className="alert alert-success">{actionMessage}</div>}
      {actionError && <div className="alert alert-error">{actionError}</div>}

      <form onSubmit={handleFilter} style={{ marginBottom: "1rem", maxWidth: 240 }}>
        <label>Filter by date</label>
        <input type="date" value={dateFilter} onChange={(e) => setDateFilter(e.target.value)} onBlur={handleFilter} />
      </form>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              {isAdminOrHR && <th>Employee</th>}
              <th>Date</th>
              <th>Check in</th>
              <th>Check out</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={isAdminOrHR ? 5 : 4} className="empty-state">Loading…</td></tr>
            )}
            {!loading && records.length === 0 && (
              <tr><td colSpan={isAdminOrHR ? 5 : 4} className="empty-state">No attendance records yet.</td></tr>
            )}
            {!loading && records.map((r) => (
              <tr key={r.id}>
                {isAdminOrHR && <td>{r.employee_name} <span style={{ color: "var(--ink-soft)" }}>({r.employee_code})</span></td>}
                <td>{r.date}</td>
                <td>{r.check_in || "—"}</td>
                <td>{r.check_out || "—"}</td>
                <td><StatusBadge value={r.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}
