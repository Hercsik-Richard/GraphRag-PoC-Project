/**
 * ChatInterface widget - Main chat component with message list and input form
 */
import { useEffect, useRef, useState } from "react";
import {
  Brain,
  CheckCircle2,
  Loader2,
  MessageCircle,
  MessageSquareText,
  Search,
} from "lucide-react";
import { useConversation } from "@/entities/conversation";
import type { SearchMode } from "@/entities/message";
import { MessageBubble } from "@/entities/message";
import { MessageForm, useSendMessage } from "@/features/send-message";
import { cn, UI_CONSTANTS } from "@/shared";
import type { ModelProvider } from "@/shared";

interface ChatInterfaceProps {
  conversationId: string | null;
  onMessageSent?: () => void;
  onEntityClick?: (entityId: string) => void;
  onRelationshipClick?: (source: string, target: string) => void;
  queryChatProvider: ModelProvider;
  queryEmbedProvider: ModelProvider;
}

export function ChatInterface({
  conversationId,
  onMessageSent,
  onEntityClick,
  onRelationshipClick,
  queryChatProvider,
  queryEmbedProvider,
}: ChatInterfaceProps) {
  const {
    messages,
    isLoading: loadingMessages,
    mutate,
  } = useConversation(conversationId);
  const { sendMessage, isSending } = useSendMessage(conversationId);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [sendError, setSendError] = useState<string | null>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  const handleSendMessage = async (content: string, searchMode: SearchMode) => {
    if (!conversationId) return;

    if (content.length > UI_CONSTANTS.MAX_MESSAGE_LENGTH) {
      setSendError(
        `A kérdés legfeljebb ${UI_CONSTANTS.MAX_MESSAGE_LENGTH} karakter lehet. Rövidítsd le, vagy bontsd több kérdésre.`
      );
      throw new Error("Message is too long");
    }

    setSendError(null);
    try {
      await sendMessage({
        question: content,
        search_mode: searchMode,
        query_chat_provider: queryChatProvider,
        query_embed_provider: queryEmbedProvider,
      });
      await mutate(); // Refresh messages after the backend saved the answer
      onMessageSent?.();
    } catch (error) {
      console.error("Failed to send message:", error);
      setSendError(formatSendError(error));
      await mutate();
      window.setTimeout(() => {
        void mutate();
      }, 5000);
      throw error;
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
                {isSending && <QueryProcessingStatus />}
                <div ref={messagesEndRef} />
              </>
            ) : isSending ? (
              <>
                <QueryProcessingStatus />
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
          errorMessage={sendError}
        />
      </div>
    </div>
  );
}

function formatSendError(error: unknown) {
  const maybeAxiosError = error as {
    response?: { status?: number; data?: { detail?: unknown; message?: unknown } };
    message?: string;
  };

  if (maybeAxiosError.response?.status === 422) {
    return `A kérdés túl hosszú vagy hibás formátumú. Maximum ${UI_CONSTANTS.MAX_MESSAGE_LENGTH} karaktert küldj.`;
  }
  if (maybeAxiosError.response?.status) {
    return `A backend nem tudta feldolgozni az üzenetet (${maybeAxiosError.response.status}).`;
  }
  return maybeAxiosError.message || "Nem sikerült elküldeni az üzenetet.";
}

const PROCESSING_STAGES = [
  {
    label: "Understanding query",
    detail: "Preparing the request for the selected model",
    icon: MessageSquareText,
    afterSeconds: 0,
  },
  {
    label: "Searching graph context",
    detail: "Collecting relevant entities and relationships",
    icon: Search,
    afterSeconds: 4,
  },
  {
    label: "Reasoning over evidence",
    detail: "Building a grounded response from the retrieved context",
    icon: Brain,
    afterSeconds: 12,
  },
  {
    label: "Finalizing answer",
    detail: "Formatting the response and source context",
    icon: CheckCircle2,
    afterSeconds: 24,
  },
] as const;

function QueryProcessingStatus() {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  useEffect(() => {
    setElapsedSeconds(0);
    const intervalId = window.setInterval(() => {
      setElapsedSeconds((seconds) => seconds + 1);
    }, 1000);

    return () => window.clearInterval(intervalId);
  }, []);

  const activeStageIndex = PROCESSING_STAGES.reduce((activeIndex, stage, index) => {
    return elapsedSeconds >= stage.afterSeconds ? index : activeIndex;
  }, 0);
  const activeStage = PROCESSING_STAGES[activeStageIndex];
  const ActiveIcon = activeStage.icon;

  return (
    <div className="mb-4 flex w-full justify-start">
      <div className="max-w-[82%] rounded-2xl border border-primary/25 bg-card px-5 py-4 text-card-foreground shadow-[0_16px_34px_rgba(43,48,64,0.12)]">
        <div className="flex items-start gap-4">
          <div className="relative mt-0.5 flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-primary/25 bg-primary/10 text-primary">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span className="absolute -right-1 -top-1 h-3 w-3 rounded-full bg-primary shadow-[0_0_0_4px_hsl(var(--primary)/0.18)]" />
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Assistant
              </span>
              <span className="rounded-md border border-primary/20 bg-primary/10 px-2 py-0.5 text-[11px] font-semibold text-primary">
                {elapsedSeconds}s
              </span>
            </div>

            <div className="mt-2 flex items-center gap-2">
              <ActiveIcon className="h-4 w-4 shrink-0 text-primary" />
              <p className="text-sm font-semibold text-foreground">
                {activeStage.label}
              </p>
              <span className="inline-flex w-5 justify-between text-primary">
                <span className="h-1 w-1 animate-bounce rounded-full bg-current [animation-delay:-0.2s]" />
                <span className="h-1 w-1 animate-bounce rounded-full bg-current [animation-delay:-0.1s]" />
                <span className="h-1 w-1 animate-bounce rounded-full bg-current" />
              </span>
            </div>

            <p className="mt-1 text-sm text-muted-foreground">
              {activeStage.detail}
            </p>

            <div className="mt-4 grid grid-cols-4 gap-1.5">
              {PROCESSING_STAGES.map((stage, index) => {
                const stageIsActive = index <= activeStageIndex;

                return (
                  <div
                    key={stage.label}
                    className={cn(
                      "h-1.5 rounded-full transition-colors",
                      stageIsActive ? "bg-primary" : "bg-muted"
                    )}
                  />
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
