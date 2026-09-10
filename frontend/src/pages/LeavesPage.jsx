import { useEffect, useState, useCallback } from "react";
import Layout from "../components/Layout";
import StatusBadge from "../components/StatusBadge";
import { useAuth } from "../context/AuthContext";
import { leavesApi } from "../api/resources";

export default function LeavesPage() {
  const { isAdminOrHR } = useAuth();
  const [requests, setRequests] = useState([]);
  const [leaveTypes, setLeaveTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [applyOpen, setApplyOpen] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [reviewComment, setReviewComment] = useState({});

  const load = useCallback(async (status = "") => {
    setLoading(true);
    try {
      const params = status ? { status } : {};
      const { data } = isAdminOrHR ? await leavesApi.list(params) : await leavesApi.myRequests(params);
      setRequests(data.results || data);
    } finally {
      setLoading(false);
    }
  }, [isAdminOrHR]);

  useEffect(() => {
    load();
    leavesApi.types().then(({ data }) => setLeaveTypes(data.results || data));
  }, [load]);

  const handleFilter = (status) => {
    setStatusFilter(status);
    load(status);
  };

  const handleCancel = async (id) => {
    await leavesApi.cancel(id);
    setFeedback("Leave request cancelled.");
    load(statusFilter);
  };

  const handleReview = async (id, action) => {
    await leavesApi.review(id, action, reviewComment[id] || "");
    setFeedback(`Leave request ${action === "APPROVE" ? "approved" : "rejected"}.`);
    load(statusFilter);
  };

  return (
    <Layout>
      <div className="page-header">
        <div>
          <h1>Leave requests</h1>
          <p>{isAdminOrHR ? "Review and act on requests from your team." : "Apply for leave and track your requests."}</p>
        </div>
        {!isAdminOrHR && (
          <button className="btn btn-accent" onClick={() => setApplyOpen(true)}>+ Apply for leave</button>
        )}
      </div>

      {feedback && <div className="alert alert-success">{feedback}</div>}

      <div style={{ display: "flex", gap: "0.4rem", marginBottom: "1rem" }}>
        {["", "PENDING", "APPROVED", "REJECTED", "CANCELLED"].map((s) => (
          <button
            key={s || "all"}
            className={`btn btn-small ${statusFilter === s ? "btn-accent" : "btn-outline"}`}
            onClick={() => handleFilter(s)}
          >
            {s || "All"}
          </button>
        ))}
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              {isAdminOrHR && <th>Employee</th>}
              <th>Type</th>
              <th>Dates</th>
              <th>Days</th>
              <th>Reason</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {loading && <tr><td colSpan={isAdminOrHR ? 7 : 6} className="empty-state">Loading…</td></tr>}
            {!loading && requests.length === 0 && (
              <tr><td colSpan={isAdminOrHR ? 7 : 6} className="empty-state">No leave requests found.</td></tr>
            )}
            {!loading && requests.map((r) => (
              <tr key={r.id}>
                {isAdminOrHR && <td>{r.employee_name} <span style={{ color: "var(--ink-soft)" }}>({r.employee_code})</span></td>}
                <td>{r.leave_type_name}</td>
                <td>{r.start_date} → {r.end_date}</td>
                <td>{r.total_days}</td>
                <td style={{ maxWidth: 220 }}>{r.reason}</td>
                <td><StatusBadge value={r.status} /></td>
                <td style={{ whiteSpace: "nowrap" }}>
                  {r.status === "PENDING" && !isAdminOrHR && (
                    <button className="btn btn-outline btn-small" onClick={() => handleCancel(r.id)}>Cancel</button>
                  )}
                  {r.status === "PENDING" && isAdminOrHR && (
                    <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
                      <input
                        placeholder="Comment (optional)"
                        value={reviewComment[r.id] || ""}
                        onChange={(e) => setReviewComment((c) => ({ ...c, [r.id]: e.target.value }))}
                        style={{ width: 130, padding: "0.3rem 0.5rem", fontSize: "0.8rem" }}
                      />
                      <button className="btn btn-success btn-small" onClick={() => handleReview(r.id, "APPROVE")}>Approve</button>
                      <button className="btn btn-danger btn-small" onClick={() => handleReview(r.id, "REJECT")}>Reject</button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {applyOpen && (
        <ApplyLeaveModal
          leaveTypes={leaveTypes}
          onClose={() => setApplyOpen(false)}
          onApplied={() => {
            setApplyOpen(false);
            setFeedback("Leave request submitted for review.");
            load(statusFilter);
          }}
        />
      )}
    </Layout>
  );
}

function ApplyLeaveModal({ leaveTypes, onClose, onApplied }) {
  const [form, setForm] = useState({ leave_type: "", start_date: "", end_date: "", reason: "" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await leavesApi.apply(form);
      onApplied();
    } catch (err) {
      const data = err.response?.data;
      setError(typeof data === "string" ? data : data?.detail || Object.values(data || {})[0] || "Could not submit request.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Apply for leave</h2>
        {error && <div className="alert alert-error">{String(error)}</div>}
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label>Leave type</label>
            <select value={form.leave_type} onChange={update("leave_type")} required>
              <option value="">Select a type…</option>
              {leaveTypes.map((t) => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>
          <div className="field-row">
            <div className="field">
              <label>Start date</label>
              <input type="date" value={form.start_date} onChange={update("start_date")} required />
            </div>
            <div className="field">
              <label>End date</label>
              <input type="date" value={form.end_date} onChange={update("end_date")} required />
            </div>
          </div>
          <div className="field">
            <label>Reason</label>
            <textarea rows={3} value={form.reason} onChange={update("reason")} required />
          </div>
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.6rem", marginTop: "1rem" }}>
            <button type="button" className="btn btn-outline" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-accent" disabled={saving}>{saving ? "Submitting…" : "Submit request"}</button>
          </div>
        </form>
      </div>
    </div>
  );
}
