import client from "./client";

export const authApi = {
  login: (username, password) => client.post("/auth/login/", { username, password }),
  logout: (refresh) => client.post("/auth/logout/", { refresh }),
};

export const employeesApi = {
  list: (params) => client.get("/employees/", { params }),
  me: () => client.get("/employees/me/"),
  get: (id) => client.get(`/employees/${id}/`),
  create: (payload) => client.post("/employees/", payload),
  update: (id, payload) => client.patch(`/employees/${id}/`, payload),
  remove: (id) => client.delete(`/employees/${id}/`),
  departments: () => client.get("/employees/departments/"),
  createDepartment: (payload) => client.post("/employees/departments/", payload),
};

export const attendanceApi = {
  list: (params) => client.get("/attendance/", { params }),
  myHistory: (params) => client.get("/attendance/my-history/", { params }),
  checkIn: () => client.post("/attendance/check-in/"),
  checkOut: () => client.post("/attendance/check-out/"),
  update: (id, payload) => client.patch(`/attendance/${id}/`, payload),
};

export const leavesApi = {
  list: (params) => client.get("/leaves/", { params }),
  myRequests: (params) => client.get("/leaves/my-requests/", { params }),
  types: () => client.get("/leaves/types/"),
  apply: (payload) => client.post("/leaves/", payload),
  cancel: (id) => client.post(`/leaves/${id}/cancel/`),
  review: (id, action, comment) => client.post(`/leaves/${id}/review/`, { action, comment }),
};
