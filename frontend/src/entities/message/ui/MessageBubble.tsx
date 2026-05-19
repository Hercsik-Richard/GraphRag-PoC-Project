/**
 * MessageBubble component - Displays a single message
 */
import { cn } from "@/shared";
import type { Message } from "@/entities/message";
import { MessageCitations } from "./MessageCitations";

interface MessageBubbleProps {
  message: Message;
  onEntityClick?: (entityId: string) => void;
  onRelationshipClick?: (source: string, target: string) => void;
}

export function MessageBubble({
  message,
  onEntityClick,
  onRelationshipClick,
}: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "mb-4 flex w-full",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "group relative max-w-[82%] rounded-2xl px-5 py-4 shadow-[0_12px_24px_rgba(43,48,64,0.08)] transition-transform",
          isUser
            ? "border border-transparent bg-secondary text-secondary-foreground"
            : "border border-border/60 bg-card text-card-foreground"
        )}
      >
        <div
          className={cn(
            "mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em]",
            isUser ? "text-secondary-foreground/70" : "text-muted-foreground"
          )}
        >
          {isUser ? "You" : "Assistant"}
        </div>
        <div className="text-sm leading-relaxed whitespace-pre-wrap wrap-break-word">
          {message.content}
        </div>

        {/* Show citations for assistant messages */}
        {!isUser && (
          <MessageCitations
            entities={message.retrieved_entities}
            relationships={message.retrieved_relationships}
            onEntityClick={onEntityClick}
            onRelationshipClick={onRelationshipClick}
          />
        )}

        <div
          className={cn(
            "mt-3 text-[11px] tracking-[0.25em] text-muted-foreground/80",
            !isUser && "border-t border-dashed border-border/50 pt-3"
          )}
        >
          {new Date(message.created_at).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}
