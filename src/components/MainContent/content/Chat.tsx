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

// Komponen animasi titik (untuk pesan temporary "Thinking...")
function TypingAnimation({ baseText }: { baseText: string }) {
  const [dots, setDots] = useState("");
  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? "" : prev + "."));
    }, 500);
    return () => clearInterval(interval);
  }, []);
  return (
    <span>
      {baseText}
      {dots}
    </span>
  );
}

export function Chat() {
  // State untuk chat messages
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

  // Setelah animasi selesai, update pesan assistant sehingga tidak lagi menampilkan animasi
  // dan mengganti teksnya dengan "Found n candidate(s)" serta mengupdate state kandidat.
  useEffect(() => {
    const finishedMsgs = messages.filter(
      (m) =>
        m.role === "assistant" &&
        m.finalText &&
        m.typedContent === m.finalText &&
        !m.content // pesan ini masih berupa pesan animasi
    );
    if (finishedMsgs.length > 0) {
      // Ambil pesan assistant yang paling baru
      const latestFinishedMsg = finishedMsgs[finishedMsgs.length - 1];
      // Update state kandidat dengan data dari pesan tersebut
      setCards(latestFinishedMsg.cardData || []);
      // Update pesan assistant agar teks animasi tergantikan dengan teks final
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
    // Bersihkan state kandidat dan suggestion sebelum memulai query baru
    setCards([]);
    setSuggestions([]);

    // Tambah pesan user
    const userMessage: ChatMessage = {
      id: Date.now(),
      role: "user",
      content: query,
    };
    setMessages((prev) => [...prev, userMessage]);

    // Tambah pesan temporary untuk assistant ("Thinking...")
    const tempAssistantMessage: ChatMessage = {
      id: Date.now() + 1,
      role: "assistant",
      content: "Thinking...",
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

      // Ambil nilai 'think', 'answer', dan 'suggestion'
      const thinkingText = data.think || "";
      const candidates: Candidate[] = data.answer || [];
      const suggestionsData: string[] = data.suggestion || [];

      // Update state suggestion (akan tampil setelah pesan final muncul)
      setSuggestions(suggestionsData);
      console.log("Candidates:", candidates);

      // Bersihkan teks thinking (jika ada tag <think>)
      const cleanThinkingText = thinkingText.replace(/<\/?think>/gi, "").trim();

      // Hapus pesan temporary "Thinking..." dan tambahkan pesan assistant baru
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

  // Handler untuk submit form (inputValue)
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

  // Cek apakah ada pesan temporary (proses thinking/animasi)
  const isThinking = messages.some((msg) => msg.isTyping);

  // Ambil pesan assistant terakhir yang sudah final (tidak temporary dan tidak sedang thinking)
  const lastAssistantMessage = messages
    .filter((m) => m.role === "assistant" && !m.isTyping)
    .slice(-1)[0];

  // Tampilkan suggestion hanya jika pesan terakhir adalah "Found n candidate(s)"
  const showSuggestions =
    lastAssistantMessage?.content?.startsWith("Found") &&
    suggestions.length > 0;

  return (
    <div className="flex h-full">
      {/* Bagian chat */}
      <div className="w-1/3 flex flex-col">
        <div className="flex-1 overflow-y-auto p-4">
          {messages
            .filter((m) => !m.cardData || m.finalText || m.content)
            .map((msg) => {
              const isAssistant = msg.role === "assistant";
              let displayText = "";

              if (isAssistant) {
                if (msg.temporary) {
                  return (
                    <div key={msg.id} className="my-4">
                      <div className="inline-block max-w-[85%] p-4 rounded-2xl bg-white text-gray-800 shadow-sm">
                        <div className="text-sm font-semibold mb-1.5">
                          SPIL Assistant
                        </div>
                        <div className="text-base whitespace-pre-wrap leading-relaxed">
                          <TypingAnimation baseText={msg.content || ""} />
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
                        ? "bg-white text-gray-800 shadow-sm"
                        : "bg-blue-600 text-white shadow"
                    }`}
                  >
                    <div className="text-sm font-semibold mb-1.5">
                      {isAssistant ? "SPIL Assistant" : "You"}
                    </div>
                    <div className="text-base whitespace-pre-wrap leading-relaxed">
                      {displayText}
                    </div>
                  </div>
                </div>
              );
            })}

          {/* Bagian suggestion hanya muncul jika pesan terakhir sudah "Found n candidate(s)" */}
          {showSuggestions && (
            <div className="mt-4">
              <div className="text-sm font-semibold mb-2">Suggestions:</div>
              <div className="flex flex-col gap-2">
                {suggestions.map((s, i) => (
                  <button
                    key={i}
                    className="w-full bg-slate-300 text-blue-500 text-left px-3 py-2 border border-blue-500 rounded hover:bg-blue-100"
                    onClick={() => handleSuggestionClick(s)}
                  >
                    <div className="flex font-medium">
                      <img
                        src="/assets/deepseek-color.svg"
                        alt=""
                        className="mr-3"
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
                className="flex-1 py-3 px-4 border rounded-2xl resize-none bg-white overflow-hidden"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
              />
              <button
                type="submit"
                className="p-3 bg-blue-600 text-white rounded-xl"
              >
                Send
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Bagian card */}
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
  );
}
