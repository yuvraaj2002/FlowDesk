const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type ChatResponse = {
  session_id: string;
  trace_id: string;
  answer_markdown: string;
  status: "answered" | "partial" | "refused" | "escalate";
  confidence: "high" | "medium" | "low";
  guardrail_flags: string[];
};

export type SessionCreateResponse = {
  session_id: string;
};

async function readError(response: Response): Promise<string> {
  const detail = await response.text();
  return detail || `Request failed (${response.status})`;
}

export async function createSession(): Promise<SessionCreateResponse> {
  const response = await fetch(`${API_BASE}/sessions/new`);
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return response.json() as Promise<SessionCreateResponse>;
}

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
    }),
  });

  if (!response.ok) {
    throw new Error(await readError(response));
  }

  return response.json() as Promise<ChatResponse>;
}
