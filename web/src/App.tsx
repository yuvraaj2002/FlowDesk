import { useMemo, useState, type FormEvent } from "react";
import { sendChat, type ChatResponse } from "./api";
import "./App.css";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  meta?: Pick<ChatResponse, "trace_id" | "status" | "confidence" | "guardrail_flags">;
};

function newSessionId(): string {
  return `sess_${crypto.randomUUID().replaceAll("-", "").slice(0, 16)}`;
}

export default function App() {
  const sessionId = useMemo(() => newSessionId(), []);
  const [accountId, setAccountId] = useState("acc_1042");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const message = input.trim();
    if (!message || loading) return;

    setError(null);
    setInput("");
    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", content: message },
    ]);
    setLoading(true);

    try {
      const data = await sendChat({
        sessionId,
        message,
        accountId: accountId.trim() || undefined,
      });
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: data.answer_markdown,
          meta: {
            trace_id: data.trace_id,
            status: data.status,
            confidence: data.confidence,
            guardrail_flags: data.guardrail_flags,
          },
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <header className="header">
        <div>
          <p className="eyebrow">FlowDesk</p>
          <h1>Support Copilot</h1>
        </div>
        <label className="account">
          Account
          <input
            value={accountId}
            onChange={(e) => setAccountId(e.target.value)}
            placeholder="acc_1042"
          />
        </label>
      </header>

      <main className="chat">
        {messages.length === 0 && (
          <p className="empty">Ask a support question. Responses come from the FastAPI `/chat` stub for now.</p>
        )}

        {messages.map((msg) => (
          <article key={msg.id} className={`bubble ${msg.role}`}>
            <p className="role">{msg.role === "user" ? "You" : "Copilot"}</p>
            <div className="content">{msg.content}</div>
            {msg.meta && (
              <p className="meta">
                {msg.meta.status} · {msg.meta.confidence} · {msg.meta.trace_id}
                {msg.meta.guardrail_flags.length > 0
                  ? ` · ${msg.meta.guardrail_flags.join(", ")}`
                  : ""}
              </p>
            )}
          </article>
        ))}

        {loading && <p className="pending">Thinking…</p>}
        {error && <p className="error">{error}</p>}
      </main>

      <form className="composer" onSubmit={onSubmit}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="How do I set up a delay step between two emails?"
          rows={3}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
