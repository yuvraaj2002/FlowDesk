const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type Citation = {
  n: number;
  chunk_id: string;
  doc_id: string;
  version: string | null;
};

export type ChatResponse = {
  session_id: string;
  trace_id: string;
  answer_markdown: string;
  citations: Citation[];
  conflict_notes: string[];
  status: "answered" | "partial" | "refused" | "escalate";
  confidence: "high" | "medium" | "low";
  proposed_actions: unknown[];
  guardrail_flags: string[];
};

export async function sendChat(params: {
  sessionId: string;
  message: string;
  accountId?: string;
}): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: params.sessionId,
      message: params.message,
      account_id: params.accountId || null,
      stream: false,
    }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed (${response.status})`);
  }

  return response.json() as Promise<ChatResponse>;
}
