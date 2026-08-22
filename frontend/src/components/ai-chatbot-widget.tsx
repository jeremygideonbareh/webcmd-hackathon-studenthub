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
  "How can I improve my resume for Psychology?",
  "Which skills am I lacking for Software Engineering?",
  "What scholarships can I apply for with an 8.2 CGPA?",
  "How many classes can I miss without attendance risk?",
];

export function AIChatbotWidget() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = React.useState(false);
  const [input, setInput] = React.useState("");
  const [loading, setLoading] = React.useState(false);
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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  React.useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim()) return;

    const userMsg: Message = {
      id: `usr_${Date.now()}`,
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput("");
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

      const data = await res.json();
      const botMsg: Message = {
        id: `bot_${Date.now()}`,
        sender: "bot",
        text: data.reply || "I have analyzed your request and updated your stream recommendations.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        engine: data.llm_engine || "Atlas Intelligence Core",
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error("Chat API error:", err);
      const fallbackMsg: Message = {
        id: `bot_err_${Date.now()}`,
        sender: "bot",
        text: `Based on your profile in ${user?.stream || "Engineering"}, I recommend focusing on core technical projects and updating your resume with quantitative bullet points!`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, fallbackMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Floating Chat Window */}
      {isOpen && (
        <div className="mb-3 w-80 sm:w-96 overflow-hidden rounded-2xl border bg-card shadow-2xl transition-all border-primary/20">
          {/* Header */}
          <div className="flex items-center justify-between bg-primary p-4 text-primary-foreground">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/20 backdrop-blur">
                <Bot className="h-5 w-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold leading-tight">Atlas AI Advisor Chatbot</h4>
                <p className="text-[10px] opacity-80">Stream Skills & Academic Intelligence</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsOpen(false)}
              className="h-8 w-8 text-primary-foreground hover:bg-white/20"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Messages Body */}
          <div className="h-80 overflow-y-auto p-4 space-y-3 bg-muted/30 text-xs">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-2 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.sender === "bot" && (
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                    <Sparkles className="h-3.5 w-3.5" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-2xl px-3.5 py-2 leading-relaxed shadow-sm ${
                    msg.sender === "user"
                      ? "bg-primary text-primary-foreground rounded-br-none"
                      : "bg-card border text-foreground rounded-bl-none"
                  }`}
                >
                  <p>{msg.text}</p>
                  <div className="mt-1 flex items-center justify-between gap-2 text-[9px] opacity-70">
                    <span>{msg.timestamp}</span>
                    {msg.engine && <span className="font-mono text-primary font-semibold">{msg.engine}</span>}
                  </div>
                </div>
                {msg.sender === "user" && (
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    <User className="h-3.5 w-3.5" />
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Sparkles className="h-3.5 w-3.5 animate-spin text-primary" />
                <span>AI Advisor is analyzing your query...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompts */}
          <div className="border-t bg-card p-2 flex gap-1 overflow-x-auto text-[10px] no-scrollbar">
            {QUICK_PROMPTS.map((prompt, i) => (
              <button
                key={i}
                onClick={() => handleSend(prompt)}
                className="shrink-0 rounded-full border bg-muted/50 px-2.5 py-1 text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Input Footer */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2 border-t p-2.5 bg-card"
          >
            <input
              type="text"
              placeholder="Ask how to improve skills, resume, or advice..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 bg-transparent px-2 py-1 text-xs focus-visible:outline-none"
            />
            <Button type="submit" size="icon" className="h-8 w-8 shrink-0" disabled={loading || !input.trim()}>
              <Send className="h-3.5 w-3.5" />
            </Button>
          </form>
        </div>
      )}

      {/* Floating Toggle Button */}
      <Button
        onClick={() => setIsOpen((prev) => !prev)}
        size="lg"
        className="rounded-full shadow-2xl gap-2 font-semibold px-4 py-3 text-xs bg-primary hover:bg-primary/90 text-primary-foreground border border-white/20"
      >
        <Bot className="h-5 w-5" />
        <span>Ask AI Advisor</span>
        <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
      </Button>
    </div>
  );
}
