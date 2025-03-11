import { useState, useEffect, useRef } from "react";

interface ChatMessage {
  id: number;
  role: "assistant" | "user";
  content?: string;
  temporary?: boolean;
  isTyping?: boolean;
  finalText?: string;
  typedContent?: string;
  keywordData?: Array<Record<string, string>>;
}

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

export function InformationChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: Date.now(),
      role: "assistant",
      content: "Hi, this is Information Chat. How can I help you today?",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const textAreaRef = useRef<HTMLTextAreaElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (textAreaRef.current) {
      textAreaRef.current.style.height = "auto";
      textAreaRef.current.style.height = `${textAreaRef.current.scrollHeight}px`;
    }
  }, [inputValue]);

  // Efek animasi mengetik untuk pesan assistant dengan finalText
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

  const sendQuery = async (query: string) => {
    // Tambahkan pesan user
    const userMessage: ChatMessage = {
      id: Date.now(),
      role: "user",
      content: query,
    };
    setMessages((prev) => [...prev, userMessage]);

    // Tambahkan pesan sementara (opsional, jika ingin menampilkan animasi "Thinking")
    const tempAssistantMessage: ChatMessage = {
      id: Date.now() + 1,
      role: "assistant",
      content: "",
      isTyping: true,
      temporary: true,
    };
    setMessages((prev) => [...prev, tempAssistantMessage]);

    try {
      const response = await fetch("http://127.0.0.1:5025/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, type: "information" }),
      });
      const data = await response.json();
      
      // Ambil data.answer dan gunakan untuk animasi mengetik
      const answerText = data.answer || "";

      setMessages((prev) => {
        // Hapus pesan yang sedang mengetik
        const filtered = prev.filter((m) => !m.isTyping);
        return [
          ...filtered,
          {
            id: Date.now(),
            role: "assistant",
            finalText: answerText,
            typedContent: "",
          },
        ];
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    await sendQuery(inputValue.trim());
    setInputValue("");
  };

  return (
    <>
      <style>{`
        @keyframes majesticBounce {
          0%, 100% { transform: translateY(0) scale(1); opacity: 1; }
          50% { transform: translateY(-12px) scale(1.3); opacity: 0.75; }
        }
        .animate-majesticBounce { animation: majesticBounce 1.5s infinite; }
      `}</style>
      <div className="flex flex-col h-full">
        {/* Conversation area full width */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => {
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
                        <MajesticTypingAnimation baseText={"Processing..."} />
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

          <div ref={messagesEndRef} />
        </div>
        {/* Input area */}
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
    </>
  );
}
