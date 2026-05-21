/**
 * Chat page - Conversations + chat with graph drawer pattern
 */
import { useMemo, useState, useCallback, useEffect, type ReactNode } from "react";
import { Database, Map, Moon, Search, Sun, Trash2 } from "lucide-react";
import { ChatInterface, ConversationList } from "@/widgets/chat-interface";
import { GraphVisualization } from "@/widgets/graph-visualization";
import { NodeDetails } from "@/widgets/node-details";
import {
  UploadButton,
  useActivateGraph,
  useDeleteCurrentIndex,
  useIndexedGraphs,
  useIndexStatus,
  type IndexedGraphStatus,
} from "@/features/upload-document";
import { useGraphData, useGraphStats, type GraphStats } from "@/entities/graph-node";
import { cn, MODEL_PROVIDER_OPTIONS, type ModelProvider } from "@/shared";

const MODEL_STORAGE_KEYS = {
  indexChat: "graphrag-index-chat-provider",
  indexEmbed: "graphrag-index-embed-provider",
  queryChat: "graphrag-query-chat-provider",
  queryEmbed: "graphrag-query-embed-provider",
} as const;

const LEGACY_MODEL_STORAGE_KEYS = {
  index: "graphrag-index-model-provider",
  query: "graphrag-query-model-provider",
} as const;

function readSavedModelProvider(key: string, fallback: ModelProvider): ModelProvider {
  const saved = window.localStorage.getItem(key);
  return MODEL_PROVIDER_OPTIONS.some((option) => option.value === saved)
    ? (saved as ModelProvider)
    : fallback;
}

function graphDisplayName(graph: IndexedGraphStatus | null | undefined) {
  if (!graph) return "No graph loaded";
  if (graph.source_filename && graph.source_filename !== "legacy-index") {
    return graph.source_filename;
  }
  if (graph.name && graph.name !== "Legacy graph") {
    return graph.name;
  }
  return "Migrated index";
}

export function ChatPage() {
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    const savedTheme = window.localStorage.getItem("graphrag-theme");
    if (savedTheme === "light" || savedTheme === "dark") return savedTheme;

    return window.matchMedia("(prefers-color-scheme: light)").matches
      ? "light"
      : "dark";
  });
  const [selectedConversationId, setSelectedConversationId] = useState<
    string | null
  >(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [isGraphOpen, setIsGraphOpen] = useState(false);
  const [indexChatProvider, setIndexChatProvider] = useState<ModelProvider>(() =>
    readSavedModelProvider(
      MODEL_STORAGE_KEYS.indexChat,
      readSavedModelProvider(LEGACY_MODEL_STORAGE_KEYS.index, "ollama")
    )
  );
  const [indexEmbedProvider, setIndexEmbedProvider] = useState<ModelProvider>(() =>
    readSavedModelProvider(MODEL_STORAGE_KEYS.indexEmbed, "ollama")
  );
  const [queryChatProvider, setQueryChatProvider] = useState<ModelProvider>(() =>
    readSavedModelProvider(
      MODEL_STORAGE_KEYS.queryChat,
      readSavedModelProvider(LEGACY_MODEL_STORAGE_KEYS.query, "ollama")
    )
  );
  const [queryEmbedProvider, setQueryEmbedProvider] = useState<ModelProvider>(() =>
    readSavedModelProvider(MODEL_STORAGE_KEYS.queryEmbed, "ollama")
  );
  const { mutate: refreshGraph } = useGraphData();
  const { stats: graphStats, mutate: refreshGraphStats } = useGraphStats();
  const { mutate: refreshIndexStatus } = useIndexStatus();
  const {
    graphs = [],
    activeGraphId,
    mutate: refreshIndexedGraphs,
  } = useIndexedGraphs();
  const activeGraph = useMemo(
    () => graphs.find((graph) => graph.id === activeGraphId) ?? null,
    [graphs, activeGraphId]
  );
  const { activateGraph, isActivating } = useActivateGraph();
  const { deleteCurrentIndex, isDeleting } = useDeleteCurrentIndex();
  const [
    highlightedNodesFromRelationship,
    setHighlightedNodesFromRelationship,
  ] = useState<string[]>([]);

  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle("dark", theme === "dark");
    root.classList.toggle("light", theme === "light");
    window.localStorage.setItem("graphrag-theme", theme);
  }, [theme]);

  useEffect(() => {
    window.localStorage.setItem(MODEL_STORAGE_KEYS.indexChat, indexChatProvider);
  }, [indexChatProvider]);

  useEffect(() => {
    window.localStorage.setItem(MODEL_STORAGE_KEYS.indexEmbed, indexEmbedProvider);
  }, [indexEmbedProvider]);

  useEffect(() => {
    window.localStorage.setItem(MODEL_STORAGE_KEYS.queryChat, queryChatProvider);
  }, [queryChatProvider]);

  useEffect(() => {
    window.localStorage.setItem(MODEL_STORAGE_KEYS.queryEmbed, queryEmbedProvider);
  }, [queryEmbedProvider]);

  const refreshGraphState = useCallback(async () => {
    await Promise.all([
      refreshGraph(),
      refreshGraphStats(),
      refreshIndexStatus(),
      refreshIndexedGraphs(),
    ]);
  }, [refreshGraph, refreshGraphStats, refreshIndexStatus, refreshIndexedGraphs]);

  const handleActivateGraph = useCallback(
    async (graphId: string) => {
      if (!graphId || graphId === activeGraphId) return;

      await activateGraph(graphId);
      setSelectedConversationId(null);
      setSelectedNodeId(null);
      setHighlightedNodesFromRelationship([]);
      await refreshGraphState();
    },
    [activeGraphId, activateGraph, refreshGraphState]
  );

  const handleUploadComplete = (graphId: string) => {
    void (async () => {
      await activateGraph(graphId);
      setSelectedConversationId(null);
      setSelectedNodeId(null);
      setHighlightedNodesFromRelationship([]);
      await refreshGraphState();
    })();
  };

  const handleDeleteCurrentGraph = async () => {
    if (!activeGraph && !graphStats?.indexed) return;
    if (!confirm("Delete the currently indexed graph?")) return;

    await deleteCurrentIndex();
    setSelectedConversationId(null);
    setSelectedNodeId(null);
    setHighlightedNodesFromRelationship([]);
    await refreshGraphState();
  };

  const handleEntityClick = useCallback((entityLabel: string) => {
    // Graph nodes use entity names/titles as IDs, so use the label directly
    setSelectedNodeId(entityLabel);
    setHighlightedNodesFromRelationship([]);
    setIsGraphOpen(true);
  }, []);

  const handleRelationshipClick = useCallback(
    (source: string, target: string) => {
      // Highlight both nodes in the relationship
      setHighlightedNodesFromRelationship([source, target]);
      setSelectedNodeId(source); // Focus on source node
      setIsGraphOpen(true);
    },
    []
  );

  const handleNodeSelect = (nodeId: string | null) => {
    setSelectedNodeId(nodeId);
    setHighlightedNodesFromRelationship([]);
  };

  const highlightedNodes = useMemo(() => {
    if (highlightedNodesFromRelationship.length > 0) {
      return highlightedNodesFromRelationship;
    }
    return selectedNodeId ? [selectedNodeId] : [];
  }, [selectedNodeId, highlightedNodesFromRelationship]);

  return (
    <div className="min-h-screen w-full bg-linear-to-br from-background via-muted/45 to-primary/10 text-foreground">
      <div className="mx-auto flex min-h-screen max-w-[96rem] flex-col gap-6 px-4 py-6 sm:px-6 lg:px-10">
        <GraphStatusBar
          graphs={graphs}
          activeGraph={activeGraph}
          graphStats={graphStats}
          isActivating={isActivating}
          isDeleting={isDeleting}
          onActivate={handleActivateGraph}
          onDelete={handleDeleteCurrentGraph}
        />

        <header className="flex flex-col gap-4 rounded-xl border border-border/70 bg-card/95 px-6 py-5 shadow-[0_18px_36px_rgba(0,0,0,0.16)] sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-muted-foreground">
              GraphRag
            </p>
            <h1 className="mt-2 text-2xl font-bold text-foreground sm:text-3xl">
              Knowledge graph assistant
            </h1>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <ModelTaskSelector
              indexChatProvider={indexChatProvider}
              indexEmbedProvider={indexEmbedProvider}
              queryChatProvider={queryChatProvider}
              queryEmbedProvider={queryEmbedProvider}
              onIndexChatProviderChange={setIndexChatProvider}
              onIndexEmbedProviderChange={setIndexEmbedProvider}
              onQueryChatProviderChange={setQueryChatProvider}
              onQueryEmbedProviderChange={setQueryEmbedProvider}
            />
            <button
              type="button"
              onClick={() =>
                setTheme((current) => (current === "dark" ? "light" : "dark"))
              }
              className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-border/70 bg-background text-foreground transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              aria-label={
                theme === "dark" ? "Switch to light mode" : "Switch to dark mode"
              }
              title={
                theme === "dark" ? "Switch to light mode" : "Switch to dark mode"
              }
            >
              {theme === "dark" ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </button>
            <button
              type="button"
              onClick={() => setIsGraphOpen(true)}
              className="inline-flex items-center gap-2 rounded-lg border border-primary/30 bg-primary/10 px-4 py-2 text-sm font-semibold text-primary transition-colors hover:bg-primary/20"
            >
              <Map className="h-4 w-4" />
              Graph view
            </button>
            <UploadButton
              indexChatProvider={indexChatProvider}
              indexEmbedProvider={indexEmbedProvider}
              onUploadComplete={handleUploadComplete}
            />
          </div>
        </header>

        <div className="flex flex-1 flex-col gap-6 lg:flex-row">
          <aside className="lg:w-72">
            <div className="h-full rounded-xl border border-border/70 bg-card/95 shadow-[0_14px_30px_rgba(0,0,0,0.14)]">
              <ConversationList
                graphId={activeGraphId}
                selectedId={selectedConversationId}
                onSelect={setSelectedConversationId}
              />
            </div>
          </aside>

          <main className="flex-1">
            <div className="flex h-full flex-col rounded-xl border border-border/70 bg-card/95 shadow-[0_20px_42px_rgba(0,0,0,0.16)]">
              <ChatInterface
                conversationId={selectedConversationId}
                queryChatProvider={queryChatProvider}
                queryEmbedProvider={queryEmbedProvider}
                onMessageSent={() => void refreshGraph()}
                onEntityClick={handleEntityClick}
                onRelationshipClick={handleRelationshipClick}
              />
            </div>
          </main>
        </div>
      </div>

      <GraphDrawer
        open={isGraphOpen}
        onClose={() => setIsGraphOpen(false)}
        highlightedNodes={highlightedNodes}
        onNodeSelect={handleNodeSelect}
        selectedNodeId={selectedNodeId}
        conversationId={selectedConversationId}
        queryChatProvider={queryChatProvider}
        queryEmbedProvider={queryEmbedProvider}
        onEntityClick={handleEntityClick}
        onRelationshipClick={handleRelationshipClick}
        onMessageSent={() => void refreshGraph()}
      />
    </div>
  );
}

function GraphStatusBar({
  graphs,
  activeGraph,
  graphStats,
  isActivating,
  isDeleting,
  onActivate,
  onDelete,
}: {
  graphs: IndexedGraphStatus[];
  activeGraph: IndexedGraphStatus | null;
  graphStats?: GraphStats;
  isActivating: boolean;
  isDeleting: boolean;
  onActivate: (graphId: string) => void;
  onDelete: () => void;
}) {
  const completedGraphs = graphs.filter((graph) => graph.status === "completed");
  const graphName = graphDisplayName(activeGraph);
  const canDelete = Boolean(activeGraph || graphStats?.indexed) && !isDeleting;
  const statusLabel =
    activeGraph?.status === "processing" || activeGraph?.status === "queued"
      ? "Indexing"
      : activeGraph || graphStats?.indexed
        ? "Active"
        : "Empty";

  return (
    <section className="flex flex-col gap-3 rounded-xl border border-border/70 bg-card/95 px-4 py-3 shadow-[0_14px_30px_rgba(0,0,0,0.12)] sm:flex-row sm:items-center sm:justify-between">
      <div className="flex min-w-0 items-center gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-primary/25 bg-primary/10 text-primary">
          <Database className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground">
            Current Graph
          </p>
          <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1">
            <select
              value={activeGraph?.id ?? ""}
              onChange={(event) => onActivate(event.target.value)}
              disabled={isActivating || completedGraphs.length === 0}
              className="max-w-full rounded-md border border-border/70 bg-background px-2 py-1 text-base font-bold text-foreground shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-60 sm:text-lg"
              aria-label="Select active indexed graph"
              title="Select active indexed graph"
            >
              {!activeGraph && <option value="">{graphName}</option>}
              {completedGraphs.map((graph) => (
                <option key={graph.id} value={graph.id}>
                  {graphDisplayName(graph)}
                </option>
              ))}
            </select>
            <span className="rounded-full border border-border/70 px-2 py-0.5 text-xs font-semibold text-muted-foreground">
              {statusLabel}
            </span>
            {isActivating && (
              <span className="text-xs font-semibold text-muted-foreground">
                Loading graph...
              </span>
            )}
          </div>
        </div>
      </div>
      <div className="flex items-center justify-between gap-3 sm:justify-end">
        <div className="text-right text-xs font-semibold text-muted-foreground">
          <span>{graphStats?.entity_count ?? 0} entities</span>
          <span className="mx-2 text-border">/</span>
          <span>{graphStats?.relationship_count ?? 0} relationships</span>
        </div>
        <button
          type="button"
          onClick={onDelete}
          disabled={!canDelete}
          className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-destructive/40 bg-destructive/10 text-destructive transition-colors hover:bg-destructive hover:text-destructive-foreground disabled:cursor-not-allowed disabled:opacity-40"
          aria-label="Delete current indexed graph"
          title="Delete current indexed graph"
        >
          {isDeleting ? (
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
          ) : (
            <Trash2 className="h-4 w-4" />
          )}
        </button>
      </div>
    </section>
  );
}

function ModelTaskSelector({
  indexChatProvider,
  indexEmbedProvider,
  queryChatProvider,
  queryEmbedProvider,
  onIndexChatProviderChange,
  onIndexEmbedProviderChange,
  onQueryChatProviderChange,
  onQueryEmbedProviderChange,
}: {
  indexChatProvider: ModelProvider;
  indexEmbedProvider: ModelProvider;
  queryChatProvider: ModelProvider;
  queryEmbedProvider: ModelProvider;
  onIndexChatProviderChange: (provider: ModelProvider) => void;
  onIndexEmbedProviderChange: (provider: ModelProvider) => void;
  onQueryChatProviderChange: (provider: ModelProvider) => void;
  onQueryEmbedProviderChange: (provider: ModelProvider) => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-2 rounded-lg border border-border/70 bg-background/80 px-3 py-2">
      <TaskModelSelect
        id="index-chat-provider"
        icon={<Database className="h-4 w-4" />}
        label="Index"
        value={indexChatProvider}
        onChange={onIndexChatProviderChange}
        title="Controls the model used for GraphRAG extraction and summarization during indexing."
      />
      <TaskModelSelect
        id="index-embed-provider"
        icon={<Database className="h-4 w-4" />}
        label="Index embed"
        value={indexEmbedProvider}
        onChange={onIndexEmbedProviderChange}
        title="Controls the embedding model used to build the vector index."
      />
      <div className="h-7 w-px bg-border/70" />
      <TaskModelSelect
        id="query-chat-provider"
        icon={<Search className="h-4 w-4" />}
        label="Query"
        value={queryChatProvider}
        onChange={onQueryChatProviderChange}
        title="Controls the model used to generate query answers."
      />
      <TaskModelSelect
        id="query-embed-provider"
        icon={<Search className="h-4 w-4" />}
        label="Query embed"
        value={queryEmbedProvider}
        onChange={onQueryEmbedProviderChange}
        title="Controls the embedding model used for query-time vector retrieval."
      />
    </div>
  );
}

function TaskModelSelect({
  id,
  icon,
  label,
  value,
  onChange,
  title,
}: {
  id: string;
  icon: ReactNode;
  label: string;
  value: ModelProvider;
  onChange: (provider: ModelProvider) => void;
  title?: string;
}) {
  return (
    <label
      htmlFor={id}
      title={title}
      className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground"
    >
      <span className="text-primary">{icon}</span>
      <span>{label}</span>
      <select
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value as ModelProvider)}
        className="h-8 rounded-md border border-border/70 bg-card px-1.5 text-xs font-semibold text-foreground shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        {MODEL_PROVIDER_OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label} ({option.detail})
          </option>
        ))}
      </select>
    </label>
  );
}

function GraphDrawer({
  open,
  onClose,
  highlightedNodes,
  onNodeSelect,
  selectedNodeId,
  conversationId,
  queryChatProvider,
  queryEmbedProvider,
  onEntityClick,
  onRelationshipClick,
  onMessageSent,
}: {
  open: boolean;
  onClose: () => void;
  highlightedNodes: string[];
  onNodeSelect: (nodeId: string | null) => void;
  selectedNodeId: string | null;
  conversationId: string | null;
  queryChatProvider: ModelProvider;
  queryEmbedProvider: ModelProvider;
  onEntityClick: (entityId: string) => void;
  onRelationshipClick: (source: string, target: string) => void;
  onMessageSent: () => void;
}) {
  return (
    <div
      className={cn(
        "fixed inset-0 z-50 overflow-hidden transition-opacity duration-500",
        open
          ? "pointer-events-auto opacity-100"
          : "pointer-events-none opacity-0"
      )}
    >
      <div
        className="absolute inset-0 bg-background/90 backdrop-blur-sm"
        onClick={onClose}
      />
      <div
        className={cn(
          "absolute inset-y-0 right-0 flex h-full w-full translate-x-full items-stretch gap-6 px-4 py-6 transition-transform duration-500 sm:px-6",
          open ? "translate-x-0" : "translate-x-full"
        )}
        style={{ background: "transparent" }}
      >
        <div
          className="flex basis-1/3 flex-col rounded-xl border border-border/70 shadow-[0_20px_44px_rgba(0,0,0,0.18)]"
          style={{ background: "hsl(var(--card))" }}
        >
          <ChatInterface
            conversationId={conversationId}
            queryChatProvider={queryChatProvider}
            queryEmbedProvider={queryEmbedProvider}
            onEntityClick={onEntityClick}
            onRelationshipClick={onRelationshipClick}
            onMessageSent={onMessageSent}
          />
        </div>
        <div
          className="flex basis-2/3 flex-col rounded-xl border border-border/70 shadow-[0_28px_70px_rgba(0,0,0,0.22)]"
          style={{ background: "hsl(var(--card))" }}
        >
          <div className="flex items-center justify-between border-b border-border/30 px-6 py-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-muted-foreground">
                Knowledge graph
              </p>
              <h2 className="text-xl font-bold text-primary">Entity network</h2>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-border/70 px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground shadow-sm transition-colors hover:bg-muted/60"
              style={{ background: "hsl(var(--card))" }}
            >
              Close
            </button>
          </div>
          <div className="flex min-h-0 flex-1 flex-col gap-4 overflow-hidden p-6">
            {/* Graph area - takes remaining space */}
            <div className="min-h-0 flex-1">
              {/* Always render GraphVisualization to preserve React Flow state - use CSS to hide */}
              <div className={open ? "h-full w-full" : "hidden"}>
                <GraphVisualization
                  onNodeSelect={onNodeSelect}
                  highlightedNodes={highlightedNodes}
                  isOpen={open}
                />
              </div>
            </div>
            {/* Node details panel - fixed height with scroll */}
            <div
              className="h-56 shrink-0 overflow-hidden rounded-xl border border-border/60 shadow-inner"
              style={{ background: "hsl(var(--card))" }}
            >
              <NodeDetails
                selectedNodeId={selectedNodeId}
                onNodeSelect={onNodeSelect}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
