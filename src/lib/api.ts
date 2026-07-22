import type { AIMessage } from "@/types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function fetchAPI(endpoint: string, options?: RequestInit) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers || {}),
      },
    });
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Fetch error on ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  getProject: () => fetchAPI("/api/project"),
  getDocuments: () => fetchAPI("/api/documents"),
  getComplianceChecks: () => fetchAPI("/api/compliance"),
  getRFIs: () => fetchAPI("/api/rfis"),
  getRisks: () => fetchAPI("/api/risks"),
  getSchedule: () => fetchAPI("/api/schedule"),
  getNotifications: () => fetchAPI("/api/dashboard/notifications"),
  getRecentActivity: () => fetchAPI("/api/dashboard/activity"),

  askCopilot: (question: string): Promise<AIMessage> => 
    fetchAPI("/api/copilot/chat", {
      method: "POST",
      body: JSON.stringify({ question }),
    }),

  uploadDocument: () => fetchAPI("/api/documents/upload", { method: "POST" }),
  runComplianceAnalysis: (data: { requirement_document_id: string; vendor_document_id: string; equipment?: string; discipline?: string }) => 
    fetchAPI("/api/compliance/analyze", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  createRFI: (data: { subject: string; question: string; discipline?: string; priority?: string; equipment?: string; location?: string; raisedBy?: string }) => 
    fetchAPI("/api/rfis", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  analyzeRFI: (rfiId?: string) => 
    fetchAPI("/api/rfis/analyze", {
      method: "POST",
      body: JSON.stringify({ rfi_id: rfiId }),
    }),

  runRiskAnalysis: () => fetchAPI("/api/risks/analyze", { method: "POST" }),
};
