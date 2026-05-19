/**
 * MessageForm component - Input form for sending messages
 */
import { useState, type FormEvent } from "react";
import { Send } from "lucide-react";
import type { SearchMode } from "@/entities/message";
import { cn, UI_CONSTANTS } from "@/shared";

interface MessageFormProps {
  onSubmit: (message: string, searchMode: SearchMode) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

const SEARCH_MODES: Array<{ value: SearchMode; label: string }> = [
  { value: "auto", label: "Auto" },
  { value: "local", label: "Local" },
  { value: "global", label: "Global" },
  { value: "drift", label: "DRIFT" },
  { value: "source", label: "Source" },
];

export function MessageForm({
  onSubmit,
  isLoading = false,
  disabled = false,
}: MessageFormProps) {
  const [message, setMessage] = useState("");
  const [searchMode, setSearchMode] = useState<SearchMode>("auto");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    if (!message.trim() || isLoading || disabled) return;

    onSubmit(message.trim(), searchMode);
    setMessage("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <div className="inline-grid w-fit grid-cols-5 rounded-lg border border-border/70 bg-muted/40 p-1">
        {SEARCH_MODES.map((mode) => (
          <button
            key={mode.value}
            type="button"
            aria-pressed={searchMode === mode.value}
            disabled={isLoading || disabled}
            onClick={() => setSearchMode(mode.value)}
            className={cn(
              "h-8 min-w-16 rounded-md border px-3 text-xs font-semibold transition-colors",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
              searchMode === mode.value
                ? "border-primary bg-primary text-primary-foreground shadow-sm ring-1 ring-primary/35"
                : "border-transparent text-muted-foreground hover:bg-background/70 hover:text-foreground",
              "disabled:pointer-events-none disabled:opacity-50"
            )}
          >
            {mode.label}
          </button>
        ))}
      </div>
      <div className="flex gap-2">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your documents..."
          disabled={isLoading || disabled}
          maxLength={UI_CONSTANTS.MAX_MESSAGE_LENGTH}
          className={cn(
            "flex-1 resize-none rounded-lg border border-input bg-background px-3 py-2",
            "text-sm placeholder:text-muted-foreground",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
            "disabled:cursor-not-allowed disabled:opacity-50",
            "min-h-[80px] max-h-[200px]"
          )}
          rows={3}
        />
        <button
          type="submit"
          disabled={!message.trim() || isLoading || disabled}
          className={cn(
            "self-end rounded-lg bg-primary px-4 py-2 text-primary-foreground",
            "hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
            "disabled:pointer-events-none disabled:opacity-50",
            "transition-colors flex items-center gap-2"
          )}
        >
          {isLoading ? (
            <>
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
              <span className="text-sm">Sending...</span>
            </>
          ) : (
            <>
              <Send className="h-4 w-4" />
              <span className="text-sm">Send</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
}
