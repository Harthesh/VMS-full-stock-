import apiClient from "./client";

export async function loginRequest(payload) {
  const { data } = await apiClient.post("/auth/login", payload);
  return data;
}

export async function fetchCurrentUser() {
  const { data } = await apiClient.get("/auth/me");
  return data;
}

