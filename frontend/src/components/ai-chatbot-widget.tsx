import * as React from "react";
import { Bot, Send, Sparkles, User, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/auth-context";

interface Message {
  id: string;
  sender: "user" | "bot";
  text: string;
  timestamp: string;
  engine?: string;
}

const QUICK_PROMPTS = [
  "Improve my resume",
  "Skills I'm missing",
  "Scholarship options",
  "Attendance advice",
];

export function AIChatbotWidget() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = React.useState(false);
  const [loading, setLoading] = React.useState(false);
  const [inputValue, setInputValue] = React.useState("");
  const [messages, setMessages] = React.useState<Message[]>([
    {
      id: "welcome",
      sender: "bot",
      text: `Hello! I'm your Atlas AI Career & Academic Advisor. Ask me anything about improving your resume, missing skills for ${
        user?.stream || "your stream"
      }, scholarships, or attendance advice!`,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);

  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const inputRef = React.useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  React.useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      // Focus input when opening
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || inputValue).trim();
    if (!query) return;

    setInputValue("");

    const userMsg: Message = {
      id: `usr_${Date.now()}`,
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: query,
          stream: user?.stream || "Engineering",
          user_skills: user?.skills || ["Python", "Git", "SQL"],
          gpa: user?.gpa || 8.2,
        }),
      });

      if (!res.ok) throw new Error(`Chat API error: ${res.status}`);

      const data = await res.json();
      const botMsg: Message = {
        id: `bot_${Date.now()}`,
        sender: "bot",
        text: data.reply || "I have analyzed your request and updated your stream recommendations.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        engine: data.llm_engine || "Atlas AI Engine",
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error("Chat API error:", err);
      const fallbackMsg: Message = {
        id: `bot_err_${Date.now()}`,
        sender: "bot",
        text: `Based on your profile in ${user?.stream || "Engineering"}, I recommend focusing on core technical projects and updating your resume with quantitative bullet points!`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        engine: "Atlas Fallback Engine",
      };
      setMessages((prev) => [...prev, fallbackMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSend();
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Floating Chat Window */}
      {isOpen && (
        <div className="mb-3 w-80 sm:w-96 overflow-hidden rounded-2xl border bg-card shadow-2xl transition-all border-primary/20 flex flex-col" style={{ maxHeight: "min(520px, calc(100vh - 120px))" }}>
          {/* Header */}
          <div className="flex items-center justify-between bg-primary px-4 py-3 text-primary-foreground shrink-0">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/20 backdrop-blur">
                <Bot className="h-5 w-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold leading-tight">Atlas AI Advisor</h4>
                <p className="text-[10px] opacity-80">Powered by Groq LPU</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="flex h-8 w-8 items-center justify-center rounded-lg text-primary-foreground/80 hover:bg-white/20 hover:text-primary-foreground transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Messages Body */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 bg-muted/20 text-xs min-h-0">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-2 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.sender === "bot" && (
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary mt-0.5">
                    <Sparkles className="h-3 w-3" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-2xl px-3 py-2 leading-relaxed shadow-sm ${
                    msg.sender === "user"
                      ? "bg-primary text-primary-foreground rounded-br-sm"
                      : "bg-card border text-foreground rounded-bl-sm"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.text}</p>
                  <div className="mt-1 flex items-center gap-2 text-[9px] opacity-60">
                    <span>{msg.timestamp}</span>
                    {msg.engine && (
                      <span className="font-mono font-semibold text-primary/80">{msg.engine}</span>
                    )}
                  </div>
                </div>
                {msg.sender === "user" && (
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground mt-0.5">
                    <User className="h-3 w-3" />
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-xs text-muted-foreground px-1">
                <div className="flex gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
                <span>AI Advisor is thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompt Chips */}
          {messages.length <= 2 && (
            <div className="border-t bg-card px-3 py-2 flex gap-1.5 overflow-x-auto no-scrollbar shrink-0">
              {QUICK_PROMPTS.map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => void handleSend(prompt)}
                  className="shrink-0 rounded-full border bg-muted/50 px-3 py-1 text-[10px] font-medium text-muted-foreground hover:bg-primary/10 hover:text-primary hover:border-primary/30 transition-colors"
                >
                  {prompt}
                </button>
              ))}
            </div>
          )}

          {/* Clean Simple Input */}
          <div className="border-t bg-card p-2 shrink-0">
            <div className="flex items-center gap-2 rounded-xl border bg-background px-3 py-1.5 focus-within:ring-2 focus-within:ring-primary/40 transition-shadow">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask Atlas AI Advisor..."
                disabled={loading}
                className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground/60 disabled:opacity-50"
              />
              <button
                onClick={() => void handleSend()}
                disabled={loading || !inputValue.trim()}
                className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Floating Toggle Button */}
      <Button
        onClick={() => setIsOpen((prev) => !prev)}
        size="lg"
        className="rounded-full shadow-2xl gap-2 font-semibold px-5 py-3 text-xs bg-primary hover:bg-primary/90 text-primary-foreground border border-white/20"
      >
        <Bot className="h-5 w-5" />
        <span>AI Advisor</span>
        <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
      </Button>
    </div>
  );
}

export default AIChatbotWidget;
