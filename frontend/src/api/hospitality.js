import apiClient from "./client";

export async function fetchHospitality(params = {}) {
  const { data } = await apiClient.get("/hospitality", { params });
  return data;
}

export async function fetchHospitalityItem(id) {
  const { data } = await apiClient.get(`/hospitality/${id}`);
  return data;
}

export async function updateHospitality(id, payload) {
  const { data } = await apiClient.patch(`/hospitality/${id}`, payload);
  return data;
}
