"use client";

import { BackgroundBeams } from "@/components/ui/background-beams";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import axios from "axios";
import { Bot, User } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useRef, useState } from "react";

interface Message {
  id: number;
  role: "user" | "bot";
  content: string;
}

interface StartChatResponse {
  session_id: string;
}

interface MessageResponse {
  message: string;
  is_complete: boolean;
}

interface YouTubeReference {
  id: string;
  title: string;
  link: string;
}

export default function ChatBot() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ChatBotContent />
    </Suspense>
  );
}

function ChatBotContent() {
  const searchParams = useSearchParams();
  const initialMessage = searchParams.get("input") || ""; // Get initial message from URL query parameter
  const router = useRouter();
  const backendUrl = "https://backend.outofbounds.live";

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [chatComplete, setChatComplete] = useState<boolean>(false);
  const [references, setReferences] = useState<YouTubeReference[] | null>(null); // Updated to hold reference results
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const initializationDone = useRef(false); // Ref to track initialization

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  useEffect(() => {
    if (initializationDone.current) return; // Prevent multiple executions
    initializationDone.current = true;

    const initializeChat = async () => {
      try {
        setIsLoading(true);
        const startResponse = await axios.post<StartChatResponse>(
          `${backendUrl}/chat/start`,
          {},
          {
            headers: {
              "Content-Type": "application/json",
            },
          }
        );
        setSessionId(startResponse.data.session_id);

        if (initialMessage) {
          setMessages((prev) => [...prev, { id: Date.now(), role: "user", content: initialMessage }]);
          const response = await axios.post<MessageResponse>(
            `${backendUrl}/chat/message`,
            {
              message: initialMessage,
              session_id: startResponse.data.session_id,
            },
            {
              headers: {
                "Content-Type": "application/json",
              },
            }
          );
          setMessages((prev) => [
            ...prev,
            {
              id: Date.now(),
              role: "bot",
              content: response.data.message,
            },
          ]);

          if (response.data.is_complete) {
            setChatComplete(true);
            await fetchReferences(startResponse.data.session_id); // Fetch references once chat is complete
          }
        }
      } catch (error) {
        console.error("Error initializing chat:", error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeChat();
  }, []); // Ensure this effect runs only once by using an empty dependency array

  const fetchReferences = async (session_id: string) => {
    try {
      const response = await axios.get(`${backendUrl}/chat/references?session_id=${session_id}`, {
        headers: {
          "Content-Type": "application/json",
        },
      });
      setReferences(response.data.youtube_results); // Assuming response contains youtube_results
    } catch (error) {
      console.error("Error fetching references:", error);
    }
  };

  const sendUserMessage = async (message: string) => {
    if (!sessionId) return;

    setMessages((prev) => [...prev, { id: Date.now(), role: "user", content: message }]);

    try {
      setIsLoading(true);
      const response = await axios.post<MessageResponse>(
        `${backendUrl}/chat/message`,
        {
          message,
          session_id: sessionId,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: "bot",
          content: response.data.message,
        },
      ]);

      if (response.data.is_complete) {
        setChatComplete(true);
        await fetchReferences(sessionId);
        // Navigate to dashboard with session_id
        router.push(`/dashboard?session_id=${sessionId}`);
      }
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    await sendUserMessage(input);
    setInput("");
  };

  useEffect(() => {
    if (chatComplete && sessionId) {
      router.push(`/dashboard?session_id=${sessionId}`);
    }
  }, [chatComplete, sessionId, router]);

  return (
    <div className="flex flex-col h-screen bg-black text-white">
      <ScrollArea className="z-10 h-screen flex-1 px-4 py-6 overflow-y-auto">
        <div className="max-w-4xl bg-gradient-to-r p-2 rounded-xl mx-auto space-y-4">
          {messages.map((m) => (
            <div
              key={m.id}
              className={cn("flex items-start space-x-2 mb-4", m.role === "user" ? "justify-end" : "justify-start")}
            >
              {m.role !== "user" && (
                <div className="w-8 h-8 rounded-full border border-zinc-700/30 text-white flex items-center justify-center">
                  <Bot size={16} />
                </div>
              )}
              <div
                className={cn(
                  "max-w-[80%] rounded-2xl px-4 py-2 border backdrop-blur-sm",
                  m.role === "user"
                    ? "border-zinc-700/20 bg-gradient-to-br from-zinc-900/90 to-zinc-800/70"
                    : "border-zinc-800/20 bg-gradient-to-br from-zinc-950/90 to-zinc-900/70"
                )}
              >
                <p className="text-base leading-relaxed whitespace-pre-wrap">{m.content}</p>
              </div>
              {m.role === "user" && (
                <div className="w-8 h-8 rounded-full border border-zinc-700/30 text-white flex items-center justify-center">
                  <User size={16} />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex items-start space-x-2 mb-4 justify-start">
              <div className="w-8 h-8 rounded-full border border-zinc-700/30 text-white flex items-center justify-center">
                <Bot size={16} />
              </div>
              <div className="max-w-[80%] rounded-2xl px-4 py-2 border backdrop-blur-sm border-zinc-800/20 bg-gradient-to-br from-zinc-950/90 to-zinc-900/70">
                <div className="flex items-center space-x-2">
                  <p className="text-zinc-400">Checking if information is complete or not</p>
                  <div className="flex space-x-1">
                    <span className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                    <span className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce [animation-delay:-0.2s]"></span>
                    <span className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce [animation-delay:-0.1s]"></span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {chatComplete && <div>{/* Navigation handled in useEffect */}</div>}
        </div>
      </ScrollArea>
      <div className="z-10 w-full">
        <form onSubmit={onSubmit} className="max-w-2xl mx-auto p-4 w-full">
          <div className="relative rounded-full overflow-hidden bg-zinc-900 border border-zinc-800 shadow-xl">
            <input
              className="input bg-transparent outline-none border-none pl-4 pr-8 py-3 w-full font-sans text-md text-zinc-100 placeholder-zinc-400"
              type="text"
              value={input}
              onChange={handleInputChange}
              placeholder="Type a message..."
            />
            <div className="absolute right-1 top-[0.2em]">
              <button
                type="submit"
                className="w-10 h-10 rounded-full bg-violet-600 hover:bg-violet-500 group shadow-xl flex items-center justify-center relative overflow-hidden"
              >
                <svg
                  className="relative z-10"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 64 64"
                  height="35"
                  width="35"
                >
                  <path
                    fill-opacity="0.01"
                    fill="white"
                    d="M63.6689 29.0491L34.6198 63.6685L0.00043872 34.6194L29.0496 1.67708e-05L63.6689 29.0491Z"
                  ></path>
                  <path
                    stroke-linejoin="round"
                    stroke-linecap="round"
                    stroke-width="3.76603"
                    stroke="white"
                    d="M42.8496 18.7067L21.0628 44.6712"
                  ></path>
                  <path
                    stroke-linejoin="round"
                    stroke-linecap="round"
                    stroke-width="3.76603"
                    stroke="white"
                    d="M26.9329 20.0992L42.85 18.7067L44.2426 34.6238"
                  ></path>
                </svg>
                <div className="w-full h-full rotate-45 absolute left-[32%] top-[32%] bg-black group-hover:-left-[100%] group-hover:-top-[100%] duration-1000"></div>
                <div className="w-full h-full -rotate-45 absolute -left-[32%] -top-[32%] group-hover:left-[100%] group-hover:top-[100%] bg-black duration-1000"></div>
              </button>
            </div>
          </div>
        </form>
      </div>
      <BackgroundBeams />
    </div>
  );
}
