import { useState, useEffect, useRef } from "react";
import { Card, Candidate } from "./Card";

interface ChatMessage {
  id: number;
  role: "assistant" | "user";
  content?: string;
  temporary?: boolean;
  isTyping?: boolean;
  finalText?: string;
  typedContent?: string;
  cardData?: Candidate[];
}

// Komponen animasi "Thinking" dengan teks dan dot animasi yang menggunakan gradasi biru ke hijau
function MajesticTypingAnimation({ baseText }: { baseText: string }) {
  return (
    <span className="flex items-center">
      <span className="text-2xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-gray-700 to-gray-500">
        {baseText}
      </span>
      <span className="flex gap-2 ml-3">
        <span
          className="w-3 h-3 bg-gradient-to-r from-gray-500 to-gray-300 rounded-full animate-majesticBounce"
          style={{ animationDelay: "0s" }}
        ></span>
        <span
          className="w-3 h-3 bg-gradient-to-r from-gray-500 to-gray-300 rounded-full animate-majesticBounce"
          style={{ animationDelay: "0.2s" }}
        ></span>
        <span
          className="w-3 h-3 bg-gradient-to-r from-gray-500 to-gray-300 rounded-full animate-majesticBounce"
          style={{ animationDelay: "0.4s" }}
        ></span>
      </span>
    </span>
  );
}

export function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: Date.now(),
      role: "assistant",
      content: "Hi, how can I help you today?",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [cards, setCards] = useState<Candidate[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const textAreaRef = useRef<HTMLTextAreaElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Scroll ke pesan terakhir
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textAreaRef.current) {
      textAreaRef.current.style.height = "auto";
      textAreaRef.current.style.height = `${textAreaRef.current.scrollHeight}px`;
    }
  }, [inputValue]);

  // Animasi teks untuk pesan assistant (jika ada animasi)
  useEffect(() => {
    const msgToAnimate = messages.find(
      (m) =>
        m.role === "assistant" &&
        m.finalText &&
        m.typedContent !== m.finalText
    );
    if (!msgToAnimate) return;

    const timer = setInterval(() => {
      const nextChar =
        msgToAnimate.finalText![msgToAnimate.typedContent!.length];
      if (!nextChar) {
        clearInterval(timer);
        return;
      }
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === msgToAnimate.id
            ? { ...msg, typedContent: msg.typedContent + nextChar }
            : msg
        )
      );
    }, 2);
    return () => clearInterval(timer);
  }, [messages]);

  // Setelah animasi selesai, update pesan assistant agar tidak lagi menampilkan animasi
  useEffect(() => {
    const finishedMsgs = messages.filter(
      (m) =>
        m.role === "assistant" &&
        m.finalText &&
        m.typedContent === m.finalText &&
        !m.content // pesan ini masih berupa pesan animasi
    );
    if (finishedMsgs.length > 0) {
      const latestFinishedMsg = finishedMsgs[finishedMsgs.length - 1];
      setCards(latestFinishedMsg.cardData || []);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === latestFinishedMsg.id
            ? {
                ...msg,
                content: `Found ${latestFinishedMsg.cardData?.length || 0} candidate(s).`,
                finalText: undefined,
                typedContent: undefined,
              }
            : msg
        )
      );
    }
  }, [messages]);

  // Fungsi untuk mengirim query ke back-end
  const sendQuery = async (query: string) => {
    // Bersihkan state kandidat dan suggestion sebelum query baru
    setCards([]);
    setSuggestions([]);

    // Tambah pesan user
    const userMessage: ChatMessage = {
      id: Date.now(),
      role: "user",
      content: query,
    };
    setMessages((prev) => [...prev, userMessage]);

    // Tambah pesan temporary untuk assistant dengan animasi megah
    const tempAssistantMessage: ChatMessage = {
      id: Date.now() + 1,
      role: "assistant",
      content: "Thinking", // tanpa "..." agar animasi dot lebih menonjol
      isTyping: true,
      temporary: true,
    };
    setMessages((prev) => [...prev, tempAssistantMessage]);

    try {
      const response = await fetch("http://127.0.0.1:5025/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await response.json();

      const thinkingText = data.think || "";
      const candidates: Candidate[] = data.answer || [];
      const suggestionsData: string[] = data.suggestion || [];

      setSuggestions(suggestionsData);
      console.log("Candidates:", candidates);

      const cleanThinkingText = thinkingText.replace(/<\/?think>/gi, "").trim();

      // Hapus pesan temporary "Thinking" dan tambahkan pesan final dari assistant
      setMessages((prev) => {
        const filtered = prev.filter((m) => !m.isTyping);
        if (cleanThinkingText) {
          return [
            ...filtered,
            {
              id: Date.now(),
              role: "assistant",
              finalText: cleanThinkingText,
              typedContent: "",
              cardData: candidates,
            },
          ];
        } else {
          return [
            ...filtered,
            {
              id: Date.now(),
              role: "assistant",
              content: `Found ${candidates.length} candidate(s).`,
              cardData: candidates,
            },
          ];
        }
      });
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => {
        const filtered = prev.filter((m) => !m.isTyping);
        return [
          ...filtered,
          {
            id: Date.now(),
            role: "assistant",
            content: "Oops! Something went wrong.",
          },
        ];
      });
    }
  };

  // Handler untuk submit form
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    await sendQuery(inputValue.trim());
    setInputValue("");
  };

  // Handler untuk klik suggestion
  const handleSuggestionClick = async (suggestion: string) => {
    await sendQuery(suggestion);
  };

  const lastAssistantMessage = messages
    .filter((m) => m.role === "assistant" && !m.isTyping)
    .slice(-1)[0];

  const showSuggestions =
    lastAssistantMessage?.content?.startsWith("Found") &&
    suggestions.length > 0;

  return (
    <>
      {/* Sisipkan keyframes animasi secara inline */}
      <style>{`
        @keyframes majesticBounce {
          0%, 100% {
            transform: translateY(0) scale(1);
            opacity: 1;
          }
          50% {
            transform: translateY(-12px) scale(1.3);
            opacity: 0.75;
          }
        }
        .animate-majesticBounce {
          animation: majesticBounce 1.5s infinite;
        }
      `}</style>
      <div className="flex h-full">
        {/* Bagian Chat */}
        <div className="w-1/3 flex flex-col">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages
              .filter((m) => !m.cardData || m.finalText || m.content)
              .map((msg) => {
                const isAssistant = msg.role === "assistant";
                let displayText = "";

                if (isAssistant) {
                  if (msg.temporary) {
                    return (
                      <div key={msg.id} className="my-4">
                        <div className="inline-block max-w-[85%] p-4 rounded-2xl bg-white text-gray-800 shadow-lg">
                          <div className="text-sm font-bold mb-2">
                            SPIL Assistant
                          </div>
                          <div className="text-base whitespace-pre-wrap leading-relaxed">
                            <MajesticTypingAnimation baseText={msg.content || ""} />
                          </div>
                        </div>
                      </div>
                    );
                  } else if (msg.finalText) {
                    displayText = msg.typedContent || "";
                  } else {
                    displayText = msg.content || "";
                  }
                } else {
                  displayText = msg.content || "";
                }

                return (
                  <div
                    key={msg.id}
                    className={`my-4 ${isAssistant ? "" : "flex justify-end"}`}
                  >
                    <div
                      className={`inline-block max-w-[85%] p-4 rounded-2xl ${
                        isAssistant
                          ? "bg-white text-gray-800 shadow-lg"
                          : "bg-blue-600 text-white shadow-md"
                      }`}
                    >
                      <div className="text-sm font-bold mb-2">
                        {isAssistant ? "SPIL Assistant" : "You"}
                      </div>
                      <div className="text-base whitespace-pre-wrap leading-relaxed">
                        {displayText}
                      </div>
                    </div>
                  </div>
                );
              })}

            {/* Bagian Suggestions */}
            {showSuggestions && (
              <div className="mt-4">
                <div className="text-sm font-bold mb-2">Suggestions:</div>
                <div className="flex flex-col gap-2">
                  {suggestions.map((s, i) => (
                    <button
                      key={i}
                      className="w-full bg-slate-300 text-blue-500 text-left px-4 py-2 border border-blue-500 rounded hover:bg-blue-100 transition"
                      onClick={() => handleSuggestionClick(s)}
                    >
                      <div className="flex items-center font-medium">
                        <img
                          src="/assets/deepseek-color.svg"
                          alt=""
                          className="mr-3 w-6 h-6"
                        />
                        {s}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
          <div className="border-t border-gray-200 p-4">
            <form onSubmit={handleSubmit}>
              <div className="flex items-center gap-2">
                <textarea
                  ref={textAreaRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Tulis pesan..."
                  rows={1}
                  className="flex-1 py-3 px-4 border rounded-2xl resize-none bg-white overflow-hidden focus:outline-none focus:ring-2 focus:ring-blue-400"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit(e);
                    }
                  }}
                />
                <button
                  type="submit"
                  className="p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition"
                >
                  Send
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Bagian Card */}
        <div className="w-2/3 border-l border-gray-200 overflow-y-auto p-4">
          {cards.length > 0 ? (
            cards.map((candidate) => (
              <Card key={candidate.id} data={candidate} />
            ))
          ) : (
            <div className="text-gray-500">No cards available.</div>
          )}
        </div>
      </div>
    </>
  );
}
