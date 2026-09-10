import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", roles: ["ADMIN", "HR", "EMPLOYEE"] },
  { to: "/employees", label: "Employees", roles: ["ADMIN", "HR"] },
  { to: "/attendance", label: "Attendance", roles: ["ADMIN", "HR", "EMPLOYEE"] },
  { to: "/leaves", label: "Leave requests", roles: ["ADMIN", "HR", "EMPLOYEE"] },
];

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const visibleItems = NAV_ITEMS.filter((item) => item.roles.includes(user?.role));

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="sidebar-brand">Meridian HR</div>
          <div className="sidebar-tag">Employee records &amp; workflows</div>
        </div>

        <ul className="nav-list">
          {visibleItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
              >
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            {user?.first_name} {user?.last_name}
            <div className="sidebar-role">{user?.role}</div>
          </div>
          <button className="btn btn-outline btn-small" style={{ color: "#e8e6df", borderColor: "#4d5760" }} onClick={handleLogout}>
            Sign out
          </button>
        </div>
      </aside>

      <main className="main">{children}</main>
    </div>
  );
}
