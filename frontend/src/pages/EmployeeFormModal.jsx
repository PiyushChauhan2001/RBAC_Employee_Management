import { useState } from "react";
import { employeesApi } from "../api/resources";

const STATUS_OPTIONS = ["ACTIVE", "ON_LEAVE", "SUSPENDED", "TERMINATED"];
const ROLE_OPTIONS = ["EMPLOYEE", "HR", "ADMIN"];

export default function EmployeeFormModal({ employee, departments, onClose, onSaved }) {
  const isEdit = Boolean(employee);
  const [form, setForm] = useState(
    isEdit
      ? {
          employee_id: employee.employee_id,
          department: employee.department || "",
          designation: employee.designation,
          phone: employee.phone || "",
          address: employee.address || "",
          date_of_joining: employee.date_of_joining,
          date_of_birth: employee.date_of_birth || "",
          salary: employee.salary || "",
          status: employee.status,
        }
      : {
          username: "",
          email: "",
          first_name: "",
          last_name: "",
          password: "",
          role: "EMPLOYEE",
          employee_id: "",
          department: "",
          designation: "",
          phone: "",
          address: "",
          date_of_joining: "",
          date_of_birth: "",
          salary: "",
          status: "ACTIVE",
        }
  );
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setErrors({});
    const payload = { ...form };
    if (payload.department === "") payload.department = null;
    if (payload.salary === "") delete payload.salary;
    if (payload.date_of_birth === "") delete payload.date_of_birth;

    try {
      if (isEdit) {
        await employeesApi.update(employee.id, payload);
        onSaved("Employee record updated.");
      } else {
        await employeesApi.create(payload);
        onSaved("Employee created successfully.");
      }
    } catch (err) {
      setErrors(err.response?.data || { detail: "Something went wrong. Please check the form and try again." });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>{isEdit ? "Edit employee" : "Add employee"}</h2>

        {errors.detail && <div className="alert alert-error">{errors.detail}</div>}

        <form onSubmit={handleSubmit}>
          {!isEdit && (
            <>
              <h3>Account</h3>
              <div className="field-row">
                <div className="field">
                  <label>First name</label>
                  <input value={form.first_name} onChange={update("first_name")} required />
                  {errors.first_name && <small style={{ color: "var(--danger)" }}>{errors.first_name}</small>}
                </div>
                <div className="field">
                  <label>Last name</label>
                  <input value={form.last_name} onChange={update("last_name")} />
                </div>
              </div>
              <div className="field-row">
                <div className="field">
                  <label>Username</label>
                  <input value={form.username} onChange={update("username")} required />
                  {errors.username && <small style={{ color: "var(--danger)" }}>{errors.username}</small>}
                </div>
                <div className="field">
                  <label>Email</label>
                  <input type="email" value={form.email} onChange={update("email")} required />
                  {errors.email && <small style={{ color: "var(--danger)" }}>{errors.email}</small>}
                </div>
              </div>
              <div className="field-row">
                <div className="field">
                  <label>Temporary password</label>
                  <input type="password" value={form.password} onChange={update("password")} required minLength={8} />
                </div>
                <div className="field">
                  <label>System role</label>
                  <select value={form.role} onChange={update("role")}>
                    {ROLE_OPTIONS.map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </div>
              </div>
              <h3>Employment details</h3>
            </>
          )}

          <div className="field-row">
            <div className="field">
              <label>Employee ID</label>
              <input value={form.employee_id} onChange={update("employee_id")} required disabled={isEdit} />
              {errors.employee_id && <small style={{ color: "var(--danger)" }}>{errors.employee_id}</small>}
            </div>
            <div className="field">
              <label>Designation</label>
              <input value={form.designation} onChange={update("designation")} required />
            </div>
          </div>

          <div className="field-row">
            <div className="field">
              <label>Department</label>
              <select value={form.department} onChange={update("department")}>
                <option value="">— None —</option>
                {departments.map((d) => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>Status</label>
              <select value={form.status} onChange={update("status")}>
                {STATUS_OPTIONS.map((s) => (
                  <option key={s} value={s}>{s.replace("_", " ")}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="field-row">
            <div className="field">
              <label>Date of joining</label>
              <input type="date" value={form.date_of_joining} onChange={update("date_of_joining")} required />
            </div>
            <div className="field">
              <label>Date of birth</label>
              <input type="date" value={form.date_of_birth} onChange={update("date_of_birth")} />
            </div>
          </div>

          <div className="field-row">
            <div className="field">
              <label>Phone</label>
              <input value={form.phone} onChange={update("phone")} placeholder="+15551234567" />
            </div>
            <div className="field">
              <label>Salary</label>
              <input type="number" step="0.01" value={form.salary} onChange={update("salary")} />
            </div>
          </div>

          <div className="field">
            <label>Address</label>
            <textarea rows={2} value={form.address} onChange={update("address")} />
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.6rem", marginTop: "1.2rem" }}>
            <button type="button" className="btn btn-outline" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-accent" disabled={saving}>
              {saving ? "Saving…" : isEdit ? "Save changes" : "Create employee"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
