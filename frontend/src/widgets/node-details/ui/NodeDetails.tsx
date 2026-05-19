/**
 * NodeDetails widget - Display detailed information about a selected node
 */
import { Info, Tag, FileText } from "lucide-react";
import { useGraphData } from "@/entities/graph-node";

interface NodeDetailsProps {
  selectedNodeId: string | null;
  onNodeSelect?: (nodeId: string) => void;
}

export function NodeDetails({
  selectedNodeId,
  onNodeSelect,
}: NodeDetailsProps) {
  const { graphData } = useGraphData();

  const selectedNode = graphData?.nodes.find(
    (node) => node.id === selectedNodeId
  );

  if (!selectedNodeId || !selectedNode) {
    return (
      <div className="flex h-full flex-col items-center justify-center px-6 text-center text-muted-foreground">
        <Info className="mb-2 h-8 w-8 text-primary opacity-70" />
        <p className="text-sm font-medium">Select a node to view details</p>
        <p className="mt-1 text-xs">
          Tap any graph entity to inspect its context.
        </p>
      </div>
    );
  }

  const { data } = selectedNode;
  const connections = graphData?.edges.filter(
    (edge) => edge.source === selectedNodeId || edge.target === selectedNodeId
  );

  const handleConnectionClick = (nodeId: string) => {
    onNodeSelect?.(nodeId);
  };

  return (
    <div className="flex h-full flex-col overflow-y-auto p-4">
      {/* Header row: Title + Type badge */}
      <div className="mb-3 flex flex-wrap items-start gap-3">
        <h3 className="wrap-break-word text-lg font-bold text-foreground">
          {data.label}
        </h3>
        <div className="inline-flex shrink-0 items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-[0.2em] text-primary">
          <Tag className="h-3 w-3" />
          {data.type}
        </div>
      </div>

      {/* Description */}
      {data.description && (
        <div className="space-y-1.5 rounded-xl border border-border/30 bg-muted/30 p-3 text-sm leading-relaxed text-muted-foreground">
          <div className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.25em] text-primary">
            <FileText className="h-3.5 w-3.5" />
            Description
          </div>
          <p className="text-xs leading-relaxed">{data.description}</p>
        </div>
      )}

      {/* Connections - show all, clickable */}
      {connections && connections.length > 0 && (
        <div className="mt-3 space-y-2">
          <div className="text-xs font-semibold text-foreground">
            Connections ({connections.length})
          </div>
          <div className="flex flex-wrap gap-2">
            {connections.map((edge) => {
              const isSource = edge.source === selectedNodeId;
              const otherNodeId = isSource ? edge.target : edge.source;
              const otherNode = graphData?.nodes.find(
                (n) => n.id === otherNodeId
              );

              return (
                <button
                  key={edge.id}
                  onClick={() => handleConnectionClick(otherNodeId)}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-border/40 bg-muted/30 px-2 py-1 text-[10px] transition-all hover:border-primary/50 hover:bg-primary/10 hover:text-primary"
                >
                  <span className="text-muted-foreground">
                    {isSource ? "→" : "←"}
                  </span>
                  <span className="font-medium">
                    {otherNode?.data.label || "Unknown"}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}
      {connections && connections.length === 0 && (
        <div className="mt-3 rounded-xl border border-border/30 bg-muted/20 p-3 text-xs text-muted-foreground">
          No confirmed GraphRAG relationships for this entity.
        </div>
      )}
    </div>
  );
}
