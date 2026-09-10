import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import { employeesApi, attendanceApi, leavesApi } from "../api/resources";
import StatusBadge from "../components/StatusBadge";

export default function DashboardPage() {
  const { user, isAdminOrHR } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [recentLeaves, setRecentLeaves] = useState([]);

  useEffect(() => {
    let cancelled = false;

    async function loadAdminData() {
      const today = new Date().toISOString().slice(0, 10);
      const [employeesRes, attendanceRes, pendingRes, recentRes] = await Promise.all([
        employeesApi.list({ page_size: 1 }),
        attendanceApi.list({ date: today, page_size: 1 }),
        leavesApi.list({ status: "PENDING", page_size: 1 }),
        leavesApi.list({ page_size: 5 }),
      ]);
      if (cancelled) return;
      setStats({
        totalEmployees: employeesRes.data.count,
        presentToday: attendanceRes.data.count,
        pendingLeaves: pendingRes.data.count,
      });
      setRecentLeaves(recentRes.data.results || []);
    }

    async function loadEmployeeData() {
      const today = new Date().toISOString().slice(0, 10);
      const [historyRes, myLeavesRes] = await Promise.all([
        attendanceApi.myHistory({ date: today }),
        leavesApi.myRequests({ page_size: 5 }),
      ]);
      if (cancelled) return;
      const todayRecord = (historyRes.data.results || historyRes.data)[0];
      setStats({
        checkedInToday: !!todayRecord?.check_in,
        checkedOutToday: !!todayRecord?.check_out,
        pendingOwnLeaves: (myLeavesRes.data.results || myLeavesRes.data).filter((l) => l.status === "PENDING").length,
      });
      setRecentLeaves(myLeavesRes.data.results || myLeavesRes.data);
    }

    (isAdminOrHR ? loadAdminData() : loadEmployeeData())
      .catch(() => {})
      .finally(() => !cancelled && setLoading(false));

    return () => {
      cancelled = true;
    };
  }, [isAdminOrHR]);

  return (
    <Layout>
      <div className="page-header">
        <div>
          <h1>Welcome back, {user?.first_name || user?.username}</h1>
          <p>Here&apos;s what&apos;s happening across the organization today.</p>
        </div>
      </div>

      {loading && <p>Loading…</p>}

      {!loading && stats && isAdminOrHR && (
        <div className="stat-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.totalEmployees}</div>
            <div className="stat-label">Total employees</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.presentToday}</div>
            <div className="stat-label">Checked in today</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.pendingLeaves}</div>
            <div className="stat-label">Leave requests awaiting review</div>
          </div>
        </div>
      )}

      {!loading && stats && !isAdminOrHR && (
        <div className="stat-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.checkedInToday ? "Yes" : "No"}</div>
            <div className="stat-label">Checked in today</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.checkedOutToday ? "Yes" : "No"}</div>
            <div className="stat-label">Checked out today</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.pendingOwnLeaves}</div>
            <div className="stat-label">Your pending leave requests</div>
          </div>
        </div>
      )}

      <h2>{isAdminOrHR ? "Recent leave activity" : "Your recent leave requests"}</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              {isAdminOrHR && <th>Employee</th>}
              <th>Type</th>
              <th>Dates</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {recentLeaves.length === 0 && (
              <tr>
                <td colSpan={isAdminOrHR ? 4 : 3} className="empty-state">
                  No leave requests yet.
                </td>
              </tr>
            )}
            {recentLeaves.map((leave) => (
              <tr key={leave.id}>
                {isAdminOrHR && <td>{leave.employee_name}</td>}
                <td>{leave.leave_type_name}</td>
                <td>
                  {leave.start_date} → {leave.end_date}
                </td>
                <td>
                  <StatusBadge value={leave.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}
