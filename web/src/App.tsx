import { useEffect, useRef, useState, type FormEvent } from "react";
import { createSession, sendChat, type ChatResponse, type Citation } from "./api";
import { applyTheme, getInitialTheme, type Theme } from "./theme";
import "./App.css";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  meta?: Pick<ChatResponse, "trace_id" | "status" | "block_reason">;
  citations?: Citation[];
};

const SUGGESTIONS = [
  "How do I set up a delay step between two emails?",
  "Where do I find billing invoices?",
  "What happens when a workflow fails mid-run?",
];

export default function App() {
  const [theme, setTheme] = useState<Theme>(() => getInitialTheme());
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionLoading, setSessionLoading] = useState(true);
  const [accountId, setAccountId] = useState("acc_1042");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const threadEnd = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  useEffect(() => {
    void startNewSession();
  }, []);

  useEffect(() => {
    threadEnd.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

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
            block_reason: data.block_reason,
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

  function useSuggestion(text: string) {
    setInput(text);
    requestAnimationFrame(() => {
      textareaRef.current?.focus();
      const el = textareaRef.current;
      if (el) {
        el.selectionStart = el.selectionEnd = text.length;
      }
    });
  }

  return (
    <div className="shell">
      <div className="stage">
        <header className="topbar">
          <div className="brand-block">
            <p className="brand">FlowDesk</p>
            <h1>Support Copilot</h1>
            <p className="session" title={sessionId ?? undefined}>
              {sessionLoading
                ? "Starting session…"
                : sessionId
                  ? sessionId
                  : "No session"}
            </p>
          </div>
          <div className="controls">
            <label className="field">
              <span>Account</span>
              <input
                value={accountId}
                onChange={(e) => setAccountId(e.target.value)}
                placeholder="acc_1042"
              />
            </label>
            <button
              type="button"
              className="ghost"
              onClick={() => void startNewSession()}
              disabled={sessionLoading || loading}
            >
              New session
            </button>
            <button
              type="button"
              className="ghost"
              onClick={() => setTheme((t) => (t === "light" ? "dark" : "light"))}
              aria-label={`Switch to ${theme === "light" ? "dark" : "light"} theme`}
            >
              {theme === "light" ? "Dark" : "Light"}
            </button>
          </div>
        </header>

        <main className="thread">
          {messages.length === 0 && !loading && (
            <div className="empty">
              <p className="empty-brand">FlowDesk</p>
              <p className="empty-title">Ask about docs, workflows, billing, or tickets.</p>
              <p className="empty-hint">
                Answers cite sources. Out-of-scope and jailbreak attempts are refused early.
              </p>
              <ul className="suggestions">
                {SUGGESTIONS.map((text) => (
                  <li key={text}>
                    <button
                      type="button"
                      className="suggestion"
                      onClick={() => useSuggestion(text)}
                      disabled={sessionLoading || !sessionId}
                    >
                      {text}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {messages.map((msg) => (
            <article key={msg.id} className={`turn ${msg.role}`}>
              {msg.role === "user" ? (
                <div className="bubble user">{msg.content}</div>
              ) : (
                <div className="answer">
                  <p className="role">Copilot</p>
                  <div className="bubble assist">{msg.content}</div>
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="sources-block">
                      <p className="sources-label">Sources</p>
                      <ul className="sources">
                        {msg.citations.map((cite) => (
                          <li key={`${cite.n}-${cite.doc_id ?? cite.source_type ?? "src"}`}>
                            <span className="src-n">[{cite.n}]</span>
                            <span className="src-doc">
                              {cite.doc_id ?? "source"}
                              {cite.source_type ? ` · ${cite.source_type}` : ""}
                              {cite.scope ? ` · ${cite.scope}` : ""}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {msg.meta && (
                    <p className="meta">
                      {msg.meta.status}
                      {msg.meta.block_reason ? ` · ${msg.meta.block_reason}` : ""}
                      {" · "}
                      {msg.meta.trace_id}
                    </p>
                  )}
                </div>
              )}
            </article>
          ))}

          {loading && (
            <div className="thinking" aria-live="polite">
              <span className="thinking-label">Thinking</span>
              <span className="thinking-dots" aria-hidden="true">
                <span />
                <span />
                <span />
              </span>
            </div>
          )}
          {error && <p className="error">{error}</p>}
          <div ref={threadEnd} />
        </main>

        <form className="composer" onSubmit={onSubmit}>
          <div className="composer-field">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about FlowDesk…"
              rows={2}
              disabled={loading || sessionLoading || !sessionId}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  e.currentTarget.form?.requestSubmit();
                }
              }}
            />
            <button
              type="submit"
              disabled={loading || sessionLoading || !sessionId || !input.trim()}
            >
              Send
            </button>
          </div>
          <p className="composer-hint">Enter to send · Shift+Enter for a new line</p>
        </form>
      </div>
    </div>
  );
}
