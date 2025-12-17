import axios from "axios";
import type {
  Campaign,
  Lead,
  DashboardStats,
  ProcessingLog,
  WorkingHoursConfig,
  WorkingHoursSettings,
  Workflow,
} from "../types";

// Base URL for the API.
// IMPORTANT: Hardcode to a RELATIVE path so the browser only ever calls the frontend origin,
// and any proxy (Vite, nginx, etc.) decides where /api is routed.
// This completely avoids leaking Docker hostnames like `backend:8000` into the browser.
const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// Campaigns
export const campaignsApi = {
  list: () => api.get<Campaign[]>("/campaigns"),
  get: (id: number) => api.get<Campaign>(`/campaigns/${id}`),
  create: (data: Partial<Campaign>) => api.post<Campaign>("/campaigns", data),
  update: (id: number, data: Partial<Campaign>) =>
    api.put<Campaign>(`/campaigns/${id}`, data),
  delete: (id: number) => api.delete(`/campaigns/${id}`),
  start: (id: number) => api.post(`/campaigns/${id}/start`),
  pause: (id: number) => api.post(`/campaigns/${id}/pause`),
  resume: (id: number) => api.post(`/campaigns/${id}/resume`),
  getLogs: (id: number) => api.get<ProcessingLog[]>(`/campaigns/${id}/logs`),
};

// Leads
export const leadsApi = {
  list: () => api.get<Lead[]>("/leads"),
  get: (id: number) => api.get<Lead>(`/leads/${id}`),
  create: (data: Partial<Lead>) => api.post<Lead>("/leads", data),
  update: (id: number, data: Partial<Lead>) =>
    api.put<Lead>(`/leads/${id}`, data),
  delete: (id: number) => api.delete(`/leads/${id}`),
  upload: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post<{ message: string; errors: string[] }>(
      "/leads/upload",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
  },
};

// Workflows
export const workflowsApi = {
  list: () => api.get<Workflow[]>("/workflows"),
  get: (id: number) => api.get<Workflow>(`/workflows/${id}`),
  create: (data: Partial<Workflow>) => api.post<Workflow>("/workflows", data),
  update: (id: number, data: Partial<Workflow>) =>
    api.put<Workflow>(`/workflows/${id}`, data),
  delete: (id: number) => api.delete(`/workflows/${id}`),
};

// Dashboard
export const dashboardApi = {
  getStats: () => api.get<DashboardStats>("/dashboard/stats"),
  getRecentCampaigns: (limit = 5) =>
    api.get<Campaign[]>(`/dashboard/recent-campaigns?limit=${limit}`),
};

// Agents
export interface Agent {
  id: number;
  name: string;
  description?: string;
  system_prompt: string;
  model: string;
  capabilities: string[];
  tools: any[];
  created_at: string;
  updated_at?: string;
}

export const agentsApi = {
  list: () => api.get<Agent[]>("/agents"),
  get: (id: number) => api.get<Agent>(`/agents/${id}`),
  create: (data: Partial<Agent>) => api.post<Agent>("/agents", data),
  update: (id: number, data: Partial<Agent>) =>
    api.put<Agent>(`/agents/${id}`, data),
  delete: (id: number) => api.delete(`/agents/${id}`),
};

// Settings
export const settingsApi = {
  getWorkingHours: () =>
    api.get<WorkingHoursSettings>("/settings/working-hours"),
  updateWorkingHours: (data: Partial<WorkingHoursConfig>) =>
    api.put<WorkingHoursSettings>("/settings/working-hours", data),
};

export default api;
