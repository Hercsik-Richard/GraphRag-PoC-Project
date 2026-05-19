/**
 * MessageBubble component - Displays a single message
 */
import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { cn } from "@/shared";
import type {
  Message,
  RetrievedEntity,
  RetrievedRelationship,
} from "@/entities/message";
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
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(formatMessageForCopy(message));
    setIsCopied(true);
    window.setTimeout(() => setIsCopied(false), 1800);
  };

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

        {!isUser && message.search_mode_used && (
          <div className="mt-3 flex flex-wrap gap-2">
            <span
              title={message.search_mode_reason ?? undefined}
              className="rounded-md border border-border/70 bg-muted/50 px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-muted-foreground"
            >
              Mode: {message.search_mode_used}
            </span>
          </div>
        )}

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
            "mt-3 flex items-center justify-between gap-3 text-[11px] text-muted-foreground/80",
            !isUser && "border-t border-dashed border-border/50 pt-3"
          )}
        >
          <span className="tracking-[0.25em]">
            {new Date(message.created_at).toLocaleTimeString()}
          </span>
          {!isUser && (
            <button
              type="button"
              onClick={handleCopy}
              className="inline-flex items-center gap-1.5 rounded-md border border-border/70 bg-muted/40 px-2 py-1 font-semibold tracking-normal text-muted-foreground transition-colors hover:border-primary/50 hover:bg-primary/10 hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              aria-label="Copy message with sources"
              title="Copy message with sources"
            >
              {isCopied ? (
                <Check className="h-3.5 w-3.5" />
              ) : (
                <Copy className="h-3.5 w-3.5" />
              )}
              <span>{isCopied ? "Copied" : "Copy"}</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function formatMessageForCopy(message: Message) {
  const parts = [message.content.trim()];
  const sources = formatSources(
    message.retrieved_entities,
    message.retrieved_relationships
  );

  if (sources) {
    parts.push(`Sources\n${sources}`);
  }

  return parts.join("\n\n");
}

function formatSources(
  entities: RetrievedEntity[] | null | undefined = [],
  relationships: RetrievedRelationship[] | null | undefined = []
) {
  const safeEntities = entities ?? [];
  const safeRelationships = relationships ?? [];

  const entityLines = safeEntities.map((entity, idx) => {
    const displayIndex = entity.index !== undefined ? entity.index : idx;
    const details = [
      entity.type && `type: ${entity.type}`,
      entity.description,
    ].filter(Boolean);

    return `- [${displayIndex}] ${entity.title ?? entity.id}${
      details.length ? ` (${details.join("; ")})` : ""
    }`;
  });

  const relationshipLines = safeRelationships.map((rel, idx) => {
    const displayIndex = rel.index !== undefined ? rel.index : idx;
    const details = [
      rel.description,
      rel.weight !== undefined && `weight: ${rel.weight}`,
    ].filter(Boolean);

    return `- [${displayIndex}] ${rel.source} -> ${rel.target}${
      details.length ? ` (${details.join("; ")})` : ""
    }`;
  });

  return [...entityLines, ...relationshipLines].join("\n");
}
