/**
 * MessageForm component - Input form for sending messages
 */
import { useState, type FormEvent } from "react";
import { Send } from "lucide-react";
import { cn, UI_CONSTANTS } from "@/shared";

interface MessageFormProps {
  onSubmit: (message: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export function MessageForm({
  onSubmit,
  isLoading = false,
  disabled = false,
}: MessageFormProps) {
  const [message, setMessage] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    if (!message.trim() || isLoading || disabled) return;

    onSubmit(message.trim());
    setMessage("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
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
    </form>
  );
}
