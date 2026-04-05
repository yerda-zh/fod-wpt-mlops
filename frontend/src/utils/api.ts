import axios from "axios";

import type { HealthResponse, HistoryEntry, PredictionResponse } from "../types/api";

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
  timeout: 60000,
});

export async function predict(file: File): Promise<PredictionResponse> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await client.post<PredictionResponse>("/predict", form);
  return data;
}

export async function getHistory(): Promise<HistoryEntry[]> {
  const { data } = await client.get<HistoryEntry[]>("/predictions");
  return data;
}

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await client.get<HealthResponse>("/health");
  return data;
}
