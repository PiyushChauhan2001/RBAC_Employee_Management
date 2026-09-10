import { useEffect, useState, useCallback } from "react";
import Layout from "../components/Layout";
import StatusBadge from "../components/StatusBadge";
import { employeesApi } from "../api/resources";
import EmployeeFormModal from "./EmployeeFormModal";

export default function EmployeesPage() {
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [feedback, setFeedback] = useState("");

  const loadEmployees = useCallback(async (query = "") => {
    setLoading(true);
    try {
      const { data } = await employeesApi.list(query ? { search: query } : {});
      setEmployees(data.results || data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadEmployees();
    employeesApi.departments().then(({ data }) => setDepartments(data.results || data));
  }, [loadEmployees]);

  const handleSearch = (e) => {
    e.preventDefault();
    loadEmployees(search);
  };

  const openCreate = () => {
    setEditingEmployee(null);
    setModalOpen(true);
  };

  const openEdit = (employee) => {
    setEditingEmployee(employee);
    setModalOpen(true);
  };

  const handleDelete = async (employee) => {
    if (!window.confirm(`Remove ${employee.user.first_name} ${employee.user.last_name}'s record? This cannot be undone.`)) return;
    await employeesApi.remove(employee.id);
    setFeedback("Employee record deleted.");
    loadEmployees(search);
  };

  const handleSaved = (message) => {
    setModalOpen(false);
    setFeedback(message);
    loadEmployees(search);
  };

  return (
    <Layout>
      <div className="page-header">
        <div>
          <h1>Employees</h1>
          <p>Every profile in the organization, searchable by name, ID, or role.</p>
        </div>
        <button className="btn btn-accent" onClick={openCreate}>
          + Add employee
        </button>
      </div>

      {feedback && <div className="alert alert-success">{feedback}</div>}

      <form onSubmit={handleSearch} style={{ marginBottom: "1rem", maxWidth: 360 }}>
        <input
          placeholder="Search by name, ID, or designation…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </form>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Employee ID</th>
              <th>Name</th>
              <th>Department</th>
              <th>Designation</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={6} className="empty-state">Loading…</td>
              </tr>
            )}
            {!loading && employees.length === 0 && (
              <tr>
                <td colSpan={6} className="empty-state">No employees found.</td>
              </tr>
            )}
            {!loading &&
              employees.map((emp) => (
                <tr key={emp.id}>
                  <td>{emp.employee_id}</td>
                  <td>{emp.user.first_name} {emp.user.last_name}</td>
                  <td>{emp.department_name || "—"}</td>
                  <td>{emp.designation}</td>
                  <td><StatusBadge value={emp.status} /></td>
                  <td style={{ whiteSpace: "nowrap" }}>
                    <button className="btn btn-outline btn-small" onClick={() => openEdit(emp)} style={{ marginRight: 6 }}>
                      Edit
                    </button>
                    <button className="btn btn-danger btn-small" onClick={() => handleDelete(emp)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {modalOpen && (
        <EmployeeFormModal
          employee={editingEmployee}
          departments={departments}
          onClose={() => setModalOpen(false)}
          onSaved={handleSaved}
        />
      )}
    </Layout>
  );
}
