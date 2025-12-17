import { useState, useEffect, useRef } from "react";
import { Button } from "../ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Input } from "../ui/input";
import { PaperAirplaneIcon, SparklesIcon } from "@heroicons/react/24/solid";
import { cn } from "../../lib/utils";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

interface PromptBuilderChatProps {
  onPromptGenerated: (prompt: any) => void;
  onDraftUpdate?: (draft: string) => void;
}

export function PromptBuilderChat({
  onPromptGenerated,
  onDraftUpdate,
}: PromptBuilderChatProps) {
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [draftPrompt, setDraftPrompt] = useState("");
  const [promptName, setPromptName] = useState("");
  const [showNameInput, setShowNameInput] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Start session on mount
  useEffect(() => {
    startSession();
  }, []);

  // Auto-scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isLoading]);

  const startSession = async () => {
    try {
      setIsLoading(true);
      const res = await fetch("/api/chat/start", { method: "POST" });
      const data = await res.json();
      setSessionId(data.id);

      // Parse messages from DB (which might be JSON strings)
      const parsedMessages = data.messages
        .filter((m: Message) => m.role !== "system")
        .map((m: Message) => {
          if (m.role === "assistant") {
            try {
              const parsed = JSON.parse(m.content);
              // Update draft if present (use the latest one)
              if (parsed.draft_prompt) {
                setDraftPrompt(parsed.draft_prompt);
                if (onDraftUpdate) {
                  onDraftUpdate(parsed.draft_prompt);
                }
              }
              return { ...m, content: parsed.message || m.content };
            } catch (e) {
              return m;
            }
          }
          return m;
        });

      setMessages(parsedMessages);
    } catch (error) {
      console.error("Failed to start chat", error);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || !sessionId) return;

    const userMsg = inputValue;
    setInputValue("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);

    // Add placeholder for streaming message
    const streamingMessageIndex = messages.length + 1;
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);
    setIsLoading(true);

    try {
      const res = await fetch(`/api/chat/${sessionId}/message/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: userMsg }),
      });

      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let streamedContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.done) {
                // Final update with parsed message and draft
                setMessages((prev) => {
                  const updated = [...prev];
                  updated[streamingMessageIndex] = {
                    role: "assistant",
                    content: data.message || streamedContent,
                  };
                  return updated;
                });

                if (data.draft_prompt) {
                  setDraftPrompt(data.draft_prompt);
                  if (onDraftUpdate) {
                    onDraftUpdate(data.draft_prompt);
                  }
                }
              } else if (data.chunk) {
                // Stream chunk
                streamedContent += data.chunk;
                setMessages((prev) => {
                  const updated = [...prev];
                  updated[streamingMessageIndex] = {
                    role: "assistant",
                    content: streamedContent,
                  };
                  return updated;
                });
              }
            } catch (e) {
              console.error("Failed to parse SSE data", e);
            }
          }
        }
      }
    } catch (error) {
      console.error("Failed to send message", error);
      // Remove placeholder on error
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!sessionId || !draftPrompt) return;
    setIsLoading(true);
    try {
      const res = await fetch(`/api/chat/${sessionId}/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          draft_prompt: draftPrompt,
          name: promptName || null,
        }),
      });
      const data = await res.json();
      onPromptGenerated(data);
      setShowNameInput(false);
    } catch (error) {
      console.error("Failed to save prompt", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="h-[600px] flex flex-col shadow-lg">
      <CardHeader className="bg-neutral-50 border-b">
        <CardTitle className="flex items-center gap-2 text-indigo-600">
          <SparklesIcon className="h-5 w-5" />
          Interactive Prompt Builder
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden p-0 bg-white">
        <div className="h-full overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={cn(
                "flex w-full",
                msg.role === "user" ? "justify-end" : "justify-start"
              )}
            >
              <div
                className={cn(
                  "max-w-[80%] rounded-2xl px-4 py-3 text-sm shadow-sm",
                  msg.role === "user"
                    ? "bg-indigo-600 text-white rounded-br-none"
                    : "bg-neutral-100 text-neutral-900 rounded-bl-none"
                )}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-neutral-100 rounded-2xl rounded-bl-none px-4 py-3">
                <div className="flex gap-1">
                  <span className="animate-bounce text-neutral-400">●</span>
                  <span className="animate-bounce delay-100 text-neutral-400">
                    ●
                  </span>
                  <span className="animate-bounce delay-200 text-neutral-400">
                    ●
                  </span>
                </div>
              </div>
            </div>
          )}
          <div ref={scrollRef} />
        </div>
      </CardContent>
      <CardFooter className="p-4 border-t gap-2 bg-neutral-50">
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Type your answer..."
          disabled={isLoading}
          className="bg-white"
        />
        <Button
          onClick={sendMessage}
          disabled={isLoading || !inputValue.trim()}
          size="icon"
        >
          <PaperAirplaneIcon className="h-4 w-4" />
        </Button>
        <Button
          variant="default"
          className="bg-green-600 hover:bg-green-700 ml-2"
          onClick={handleSave}
          disabled={isLoading || !draftPrompt}
        >
          Save Prompt
        </Button>
      </CardFooter>
    </Card>
  );
}
