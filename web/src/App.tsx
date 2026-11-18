import { useEffect, useState, type FormEvent } from "react";
import { createSession, sendChat, type ChatResponse, type Citation } from "./api";
import { applyTheme, getInitialTheme, type Theme } from "./theme";
import "./App.css";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  meta?: Pick<ChatResponse, "trace_id" | "status" | "confidence" | "guardrail_flags">;
  citations?: Citation[];
};

export default function App() {
  const [theme, setTheme] = useState<Theme>(() => getInitialTheme());
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionLoading, setSessionLoading] = useState(true);
  const [accountId, setAccountId] = useState("acc_1042");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  useEffect(() => {
    void startNewSession();
  }, []);

  function toggleTheme() {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  }

  async function startNewSession() {
    setSessionLoading(true);
    setError(null);
    try {
      const data = await createSession();
      setSessionId(data.session_id);
      setMessages([]);
      setInput("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create session");
      setSessionId(null);
    } finally {
      setSessionLoading(false);
    }
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const message = input.trim();
    if (!message || loading || !sessionId) return;

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
          citations: data.citations ?? [],
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
          <p className="session-id">
            {sessionLoading
              ? "Starting session…"
              : sessionId
                ? `Session ${sessionId}`
                : "No session"}
          </p>
        </div>
        <div className="header-actions">
          <label className="account">
            Account
            <input
              value={accountId}
              onChange={(e) => setAccountId(e.target.value)}
              placeholder="acc_1042"
            />
          </label>
          <button
            type="button"
            className="theme-toggle"
            onClick={() => void startNewSession()}
            disabled={sessionLoading || loading}
          >
            New Session
          </button>
          <button
            type="button"
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === "light" ? "dark" : "light"} theme`}
          >
            {theme === "light" ? "Dark" : "Light"}
          </button>
        </div>
      </header>

      <main className="chat">
        {messages.length === 0 && (
          <p className="empty">
            Ask a support question. Answers are grounded in retrieved docs via dense RAG + Ollama.
          </p>
        )}

        {messages.map((msg) => (
          <article key={msg.id} className={`bubble ${msg.role}`}>
            <p className="role">{msg.role === "user" ? "You" : "Copilot"}</p>
            <div className="content">{msg.content}</div>
            {msg.citations && msg.citations.length > 0 && (
              <ul className="citations">
                {msg.citations.map((cite) => (
                  <li key={`${cite.n}-${cite.chunk_id}`}>
                    [{cite.n}] {cite.doc_id ?? cite.chunk_id}
                    {cite.version ? ` ${cite.version}` : ""}
                    {cite.source_type ? ` · ${cite.source_type}` : ""}
                    {cite.score != null ? ` · ${cite.score.toFixed(2)}` : ""}
                  </li>
                ))}
              </ul>
            )}
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
          disabled={loading || sessionLoading || !sessionId}
        />
        <button type="submit" disabled={loading || sessionLoading || !sessionId || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
