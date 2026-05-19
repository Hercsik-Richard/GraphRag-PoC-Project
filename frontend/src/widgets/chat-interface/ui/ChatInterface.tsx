/**
 * ChatInterface widget - Main chat component with message list and input form
 */
import { useEffect, useRef } from "react";
import { MessageCircle } from "lucide-react";
import { useConversation } from "@/entities/conversation";
import type { Message, SearchMode } from "@/entities/message";
import { MessageBubble } from "@/entities/message";
import { MessageForm, useSendMessage } from "@/features/send-message";

interface ChatInterfaceProps {
  conversationId: string | null;
  onMessageSent?: () => void;
  onEntityClick?: (entityId: string) => void;
  onRelationshipClick?: (source: string, target: string) => void;
}

export function ChatInterface({
  conversationId,
  onMessageSent,
  onEntityClick,
  onRelationshipClick,
}: ChatInterfaceProps) {
  const {
    messages,
    isLoading: loadingMessages,
    mutate,
  } = useConversation(conversationId);
  const { sendMessage, isSending } = useSendMessage(conversationId);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  const pendingMessage: Message = {
    id: "pending-assistant-response",
    conversation_id: conversationId ?? "",
    role: "assistant",
    content: "Working on the answer...",
    created_at: new Date().toISOString(),
  };

  const handleSendMessage = async (content: string, searchMode: SearchMode) => {
    if (!conversationId) return;

    try {
      await sendMessage({ question: content, search_mode: searchMode });
      await mutate(); // Refresh messages after the backend saved the answer
      onMessageSent?.();
    } catch (error) {
      console.error("Failed to send message:", error);
      await mutate();
      window.setTimeout(() => {
        void mutate();
      }, 5000);
    }
  };

  if (!conversationId) {
    return (
      <div className="flex h-full flex-col items-center justify-center rounded-xl border border-dashed border-border/60 bg-card px-8 text-center text-muted-foreground">
        <MessageCircle className="mb-4 h-16 w-16 text-primary opacity-70" />
        <p className="text-lg font-semibold text-foreground">
          Start exploring your knowledge base
        </p>
        <p className="mt-2 text-sm">
          Create or select a conversation to unlock tailored responses and graph
          insights.
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col gap-4 p-6">
      <div className="flex-1 overflow-hidden rounded-xl border border-border/60 bg-card shadow-[0_18px_36px_rgba(0,0,0,0.14)]">
        {/* Messages area */}
        <div className="relative flex h-full flex-col">
          <div className="pointer-events-none absolute inset-x-0 top-0 h-16 bg-linear-to-b from-primary/10 via-background/35 to-transparent" />
          <div className="relative flex-1 space-y-4 overflow-y-auto px-6 py-6">
            {loadingMessages ? (
              <div className="flex h-full items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
              </div>
            ) : messages && messages.length > 0 ? (
              <>
                {messages.map((message) => (
                  <MessageBubble
                    key={message.id}
                    message={message}
                    onEntityClick={onEntityClick}
                    onRelationshipClick={onRelationshipClick}
                  />
                ))}
                {isSending && <MessageBubble message={pendingMessage} />}
                <div ref={messagesEndRef} />
              </>
            ) : isSending ? (
              <>
                <MessageBubble message={pendingMessage} />
                <div ref={messagesEndRef} />
              </>
            ) : (
              <div className="flex h-full flex-col items-center justify-center text-muted-foreground">
                <p className="text-sm">No messages yet. Ask a question.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Input form */}
      <div className="rounded-xl border border-border/60 bg-card p-4 shadow-[0_14px_30px_rgba(0,0,0,0.12)]">
        <MessageForm
          onSubmit={handleSendMessage}
          isLoading={isSending}
          disabled={!conversationId}
        />
      </div>
    </div>
  );
}
