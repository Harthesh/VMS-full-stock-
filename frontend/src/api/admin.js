import apiClient from "./client";

export async function fetchUsers() {
  const { data } = await apiClient.get("/users");
  return data;
}

export async function fetchUserDirectory() {
  const { data } = await apiClient.get("/users/directory");
  return data;
}

export async function createUser(payload) {
  const { data } = await apiClient.post("/users", payload);
  return data;
}

export async function updateUser(id, payload) {
  const { data } = await apiClient.patch(`/users/${id}`, payload);
  return data;
}

export async function fetchRoles() {
  const { data } = await apiClient.get("/users/roles");
  return data;
}

export async function createRole(payload) {
  const { data } = await apiClient.post("/users/roles", payload);
  return data;
}

export async function updateRole(id, payload) {
  const { data } = await apiClient.patch(`/users/roles/${id}`, payload);
  return data;
}

export async function fetchDepartments() {
  const { data } = await apiClient.get("/users/departments");
  return data;
}
