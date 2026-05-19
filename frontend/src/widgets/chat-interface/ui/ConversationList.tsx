/**
 * ConversationList widget - Sidebar with list of conversations
 */
import { Plus, Trash2, MessageSquare } from "lucide-react";
import { cn } from "@/shared";
import {
  useConversations,
  useCreateConversation,
  useDeleteConversation,
  type Conversation,
} from "@/entities/conversation";

interface ConversationListProps {
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function ConversationList({
  selectedId,
  onSelect,
}: ConversationListProps) {
  const { conversations, isLoading, mutate } = useConversations();
  const { createConversation, isCreating } = useCreateConversation();
  const { deleteConversation, isDeleting } = useDeleteConversation();

  const handleCreate = async () => {
    try {
      const newConv = await createConversation({
        title: `New Conversation ${new Date().toLocaleTimeString()}`,
      });
      mutate(); // Refresh list
      if (newConv) {
        onSelect(newConv.id);
      }
    } catch (error) {
      console.error("Failed to create conversation:", error);
    }
  };

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();

    if (!confirm("Delete this conversation?")) return;

    try {
      await deleteConversation(id);
      mutate(); // Refresh list
      if (selectedId === id) {
        onSelect(conversations?.[0]?.id ?? "");
      }
    } catch (error) {
      console.error("Failed to delete conversation:", error);
    }
  };

  return (
    <div className="relative flex h-full flex-col overflow-hidden rounded-xl">
      <div className="pointer-events-none absolute inset-0 bg-linear-to-b from-muted/35 via-background/35 to-primary/10" />

      <div className="relative z-10 flex h-full flex-col">
        {/* Header */}
        <div className="border-b border-border/60 bg-card px-5 py-4">
          <div className="mb-4 space-y-1">
            <h2 className="text-lg font-semibold text-foreground">
              Conversations
            </h2>
            <p className="text-xs text-muted-foreground">
              Switch between GraphRag threads or start a new query.
            </p>
          </div>
          <button
            onClick={handleCreate}
            disabled={isCreating}
            className={cn(
              "inline-flex w-full items-center justify-center gap-2 rounded-lg border border-primary/25",
              "bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground",
              "shadow-[0_10px_20px_rgba(0,0,0,0.16)] transition-all duration-200",
              "hover:-translate-y-0.5 hover:bg-primary/95",
              "disabled:translate-y-0 disabled:opacity-60 disabled:shadow-none"
            )}
          >
            <Plus className="h-4 w-4" />
            New Chat
          </button>
        </div>

        {/* Conversation list */}
        <div className="flex-1 overflow-y-auto px-4 py-3">
          {isLoading ? (
            <div className="flex h-full items-center justify-center">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            </div>
          ) : conversations && conversations.length > 0 ? (
            <div className="space-y-2">
              {conversations.map((conv) => (
                <ConversationItem
                  key={conv.id}
                  conversation={conv}
                  isSelected={selectedId === conv.id}
                  onSelect={() => onSelect(conv.id)}
                  onDelete={(e) => handleDelete(e, conv.id)}
                  isDeleting={isDeleting}
                />
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border/60 bg-card py-10 text-center text-sm text-muted-foreground">
              <MessageSquare className="mb-3 h-12 w-12 opacity-50" />
              <p>No conversations yet</p>
              <p className="mt-1 text-xs">
                Start a new chat to build a knowledge trail.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

interface ConversationItemProps {
  conversation: Conversation;
  isSelected: boolean;
  onSelect: () => void;
  onDelete: (e: React.MouseEvent) => void;
  isDeleting: boolean;
}

function ConversationItem({
  conversation,
  isSelected,
  onSelect,
  onDelete,
  isDeleting,
}: ConversationItemProps) {
  return (
    <button
      onClick={onSelect}
      className={cn(
        "group relative flex w-full items-center gap-3 overflow-hidden rounded-lg border",
        "px-4 py-3 text-left transition-all duration-200",
        isSelected
          ? "border-primary/50 bg-primary/12 text-primary"
          : "border-border/40 bg-card text-foreground hover:-translate-y-0.5 hover:border-primary/25 hover:bg-primary/10"
      )}
    >
      <div className="flex-1 min-w-0">
        <p className="truncate text-sm font-semibold">{conversation.title}</p>
        <p className="truncate text-[11px] uppercase tracking-[0.2em] text-muted-foreground/80">
          {new Date(conversation.updated_at).toLocaleDateString()}
        </p>
      </div>
      <button
        onClick={onDelete}
        disabled={isDeleting}
        className={cn(
          "relative flex h-8 w-8 items-center justify-center rounded-lg border border-destructive/40 bg-card",
          "text-destructive transition-all duration-200",
          "hover:bg-destructive hover:text-destructive-foreground",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-destructive",
          "disabled:cursor-not-allowed disabled:opacity-50",
          !isSelected && "group-hover:translate-x-1"
        )}
        title="Delete conversation"
      >
        <Trash2 className="h-3.5 w-3.5" />
      </button>
    </button>
  );
}
