/**
 * GraphVisualization widget - React Flow graph visualization
 */
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  useReactFlow,
  ReactFlowProvider,
  type Node,
  type Edge,
  type NodeMouseHandler,
} from "reactflow";
import "reactflow/dist/style.css";
import { Eye, GitBranch, Maximize2, Minimize2, Network } from "lucide-react";
import { useGraphData } from "@/entities/graph-node";
import type { GraphApiEdge, GraphApiNode } from "@/entities/graph-node";
import { CustomEdge } from "./CustomEdge";

interface GraphVisualizationProps {
  onNodeSelect?: (nodeId: string | null) => void;
  highlightedNodes?: string[];
  isOpen?: boolean;
}

type GraphViewMode = "main" | "connected" | "all";

type VisibleGraphData = {
  nodes: GraphApiNode[];
  edges: GraphApiEdge[];
};

type GraphPosition = {
  x: number;
  y: number;
};

type LayoutComponent = {
  nodeIds: string[];
  edgeCount: number;
  width: number;
  height: number;
  relativePositions: Map<string, GraphPosition>;
};

const NODE_WIDTH = 190;
const NODE_HEIGHT = 92;
const NODE_SPACING_X = 250;
const NODE_SPACING_Y = 150;
const COMPONENT_GAP_X = 320;
const COMPONENT_GAP_Y = 260;
const LAYOUT_ROW_WIDTH = 2600;

const graphColor = (name: string) => `hsl(var(${name}))`;

function getNodeColor(type: string, isHighlighted: boolean) {
  if (isHighlighted) return graphColor("--graph-edge-highlight");

  switch (type?.toUpperCase()) {
    case "PERSON":
      return graphColor("--graph-node-person");
    case "GEO":
      return graphColor("--graph-node-geo");
    case "ORGANIZATION":
      return graphColor("--graph-node-organization");
    case "EVENT":
      return graphColor("--graph-node-event");
    default:
      return graphColor("--graph-node-default");
  }
}

function getBorderColor(type: string, isHighlighted: boolean) {
  if (isHighlighted) return graphColor("--accent");

  switch (type?.toUpperCase()) {
    case "PERSON":
      return graphColor("--graph-node-person");
    case "GEO":
      return graphColor("--graph-node-geo");
    case "ORGANIZATION":
      return graphColor("--graph-node-organization");
    case "EVENT":
      return graphColor("--graph-node-event");
    default:
      return graphColor("--graph-edge");
  }
}

function createReadableLayout(graph: VisibleGraphData): Map<string, GraphPosition> {
  const nodeIds = new Set(graph.nodes.map((node) => node.id));
  const nodesById = new Map(graph.nodes.map((node) => [node.id, node]));
  const adjacency = new Map<string, Set<string>>();

  graph.nodes.forEach((node) => adjacency.set(node.id, new Set()));
  graph.edges.forEach((edge) => {
    if (!nodeIds.has(edge.source) || !nodeIds.has(edge.target)) return;

    adjacency.get(edge.source)?.add(edge.target);
    adjacency.get(edge.target)?.add(edge.source);
  });

  const seen = new Set<string>();
  const connectedComponents: LayoutComponent[] = [];
  const isolatedNodes: GraphApiNode[] = [];

  graph.nodes.forEach((node) => {
    if (seen.has(node.id)) return;

    const stack = [node.id];
    const componentIds: string[] = [];
    seen.add(node.id);

    while (stack.length > 0) {
      const current = stack.pop()!;
      componentIds.push(current);

      adjacency.get(current)?.forEach((neighbor) => {
        if (!seen.has(neighbor)) {
          seen.add(neighbor);
          stack.push(neighbor);
        }
      });
    }

    const componentEdges = graph.edges.filter(
      (edge) =>
        componentIds.includes(edge.source) && componentIds.includes(edge.target)
    );

    if (componentIds.length === 1 && componentEdges.length === 0) {
      const isolated = nodesById.get(componentIds[0]);
      if (isolated) isolatedNodes.push(isolated);
      return;
    }

    const componentNodes = componentIds
      .map((nodeId) => nodesById.get(nodeId))
      .filter((componentNode): componentNode is GraphApiNode => Boolean(componentNode));

    connectedComponents.push(
      layoutConnectedComponent(componentNodes, componentEdges, adjacency)
    );
  });

  connectedComponents.sort(
    (a, b) => b.nodeIds.length - a.nodeIds.length || b.edgeCount - a.edgeCount
  );

  if (isolatedNodes.length > 0) {
    connectedComponents.push(layoutIsolatedNodes(isolatedNodes));
  }

  return packLayoutComponents(connectedComponents);
}

function layoutConnectedComponent(
  componentNodes: GraphApiNode[],
  componentEdges: GraphApiEdge[],
  adjacency: Map<string, Set<string>>
): LayoutComponent {
  const nodeCount = componentNodes.length;
  const positions = new Map<string, GraphPosition>();

  if (nodeCount === 1) {
    positions.set(componentNodes[0].id, { x: 0, y: 0 });
    return {
      nodeIds: [componentNodes[0].id],
      edgeCount: componentEdges.length,
      width: NODE_WIDTH + NODE_SPACING_X,
      height: NODE_HEIGHT + NODE_SPACING_Y,
      relativePositions: positions,
    };
  }

  const sortedNodes = [...componentNodes].sort(
    (a, b) =>
      (adjacency.get(b.id)?.size ?? 0) - (adjacency.get(a.id)?.size ?? 0) ||
      a.id.localeCompare(b.id)
  );

  const initialRadius = Math.max(260, Math.sqrt(nodeCount) * 135);
  sortedNodes.forEach((node, index) => {
    const angle = (2 * Math.PI * index) / nodeCount;
    const radius = initialRadius * (0.78 + (index % 3) * 0.12);
    positions.set(node.id, {
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
    });
  });

  const linkedPairs = componentEdges
    .filter((edge) => positions.has(edge.source) && positions.has(edge.target))
    .map((edge) => [edge.source, edge.target] as const);

  for (let iteration = 0; iteration < 260; iteration += 1) {
    const alpha = 1 - iteration / 260;
    const ids = sortedNodes.map((node) => node.id);

    for (let i = 0; i < ids.length; i += 1) {
      for (let j = i + 1; j < ids.length; j += 1) {
        const first = positions.get(ids[i])!;
        const second = positions.get(ids[j])!;
        let dx = second.x - first.x;
        let dy = second.y - first.y;
        let distance = Math.hypot(dx, dy);

        if (distance < 1) {
          dx = 1;
          dy = 0;
          distance = 1;
        }

        const repel = (9000 * alpha) / Math.max(distance * distance, 100);
        const pushX = (dx / distance) * repel;
        const pushY = (dy / distance) * repel;
        first.x -= pushX;
        first.y -= pushY;
        second.x += pushX;
        second.y += pushY;

        const minDistance = 205;
        if (distance < minDistance) {
          const overlap = ((minDistance - distance) / 2) * alpha;
          const overlapX = (dx / distance) * overlap;
          const overlapY = (dy / distance) * overlap;
          first.x -= overlapX;
          first.y -= overlapY;
          second.x += overlapX;
          second.y += overlapY;
        }
      }
    }

    linkedPairs.forEach(([source, target]) => {
      const sourcePosition = positions.get(source)!;
      const targetPosition = positions.get(target)!;
      const dx = targetPosition.x - sourcePosition.x;
      const dy = targetPosition.y - sourcePosition.y;
      const distance = Math.max(Math.hypot(dx, dy), 1);
      const preferredDistance = 290;
      const force = (distance - preferredDistance) * 0.018 * alpha;
      const forceX = (dx / distance) * force;
      const forceY = (dy / distance) * force;

      sourcePosition.x += forceX;
      sourcePosition.y += forceY;
      targetPosition.x -= forceX;
      targetPosition.y -= forceY;
    });

    positions.forEach((position) => {
      position.x *= 0.996;
      position.y *= 0.996;
    });
  }

  return normalizeComponentPositions(
    sortedNodes.map((node) => node.id),
    componentEdges.length,
    positions
  );
}

function layoutIsolatedNodes(isolatedNodes: GraphApiNode[]): LayoutComponent {
  const positions = new Map<string, GraphPosition>();
  const columns = Math.max(1, Math.ceil(Math.sqrt(isolatedNodes.length * 1.7)));

  isolatedNodes
    .slice()
    .sort((a, b) => a.id.localeCompare(b.id))
    .forEach((node, index) => {
      const column = index % columns;
      const row = Math.floor(index / columns);
      positions.set(node.id, {
        x: column * NODE_SPACING_X,
        y: row * NODE_SPACING_Y,
      });
    });

  const rows = Math.ceil(isolatedNodes.length / columns);

  return {
    nodeIds: isolatedNodes.map((node) => node.id),
    edgeCount: 0,
    width: Math.max(NODE_WIDTH * 2, columns * NODE_SPACING_X + NODE_WIDTH),
    height: Math.max(NODE_HEIGHT * 2, rows * NODE_SPACING_Y + NODE_HEIGHT),
    relativePositions: positions,
  };
}

function normalizeComponentPositions(
  nodeIds: string[],
  edgeCount: number,
  positions: Map<string, GraphPosition>
): LayoutComponent {
  let minX = Number.POSITIVE_INFINITY;
  let maxX = Number.NEGATIVE_INFINITY;
  let minY = Number.POSITIVE_INFINITY;
  let maxY = Number.NEGATIVE_INFINITY;

  positions.forEach((position) => {
    minX = Math.min(minX, position.x);
    maxX = Math.max(maxX, position.x);
    minY = Math.min(minY, position.y);
    maxY = Math.max(maxY, position.y);
  });

  const padding = 180;
  const normalized = new Map<string, GraphPosition>();
  positions.forEach((position, nodeId) => {
    normalized.set(nodeId, {
      x: position.x - minX + padding,
      y: position.y - minY + padding,
    });
  });

  return {
    nodeIds,
    edgeCount,
    width: Math.max(maxX - minX + padding * 2 + NODE_WIDTH, NODE_WIDTH * 2),
    height: Math.max(maxY - minY + padding * 2 + NODE_HEIGHT, NODE_HEIGHT * 2),
    relativePositions: normalized,
  };
}

function packLayoutComponents(
  components: LayoutComponent[]
): Map<string, GraphPosition> {
  const packedPositions = new Map<string, GraphPosition>();
  let cursorX = 0;
  let cursorY = 0;
  let rowHeight = 0;

  components.forEach((component) => {
    if (
      cursorX > 0 &&
      cursorX + component.width > LAYOUT_ROW_WIDTH &&
      component.nodeIds.length > 1
    ) {
      cursorX = 0;
      cursorY += rowHeight + COMPONENT_GAP_Y;
      rowHeight = 0;
    }

    component.relativePositions.forEach((position, nodeId) => {
      packedPositions.set(nodeId, {
        x: cursorX + position.x,
        y: cursorY + position.y,
      });
    });

    cursorX += component.width + COMPONENT_GAP_X;
    rowHeight = Math.max(rowHeight, component.height);
  });

  return packedPositions;
}

function GraphVisualizationInner({
  onNodeSelect,
  highlightedNodes = [],
  isOpen = true,
}: GraphVisualizationProps) {
  const { graphData, isLoading, isError } = useGraphData();
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const { fitView } = useReactFlow();
  const previousHighlightedRef = useRef<string[]>([]);
  const hasInitializedRef = useRef(false);
  const graphContainerRef = useRef<HTMLDivElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Define custom edge types
  const edgeTypes = useMemo(() => ({ custom: CustomEdge }), []);
  const [viewMode, setViewMode] = useState<GraphViewMode>("main");

  const visibleGraphData = useMemo(() => {
    if (!graphData) return null;

    const highlightedNodeIds = new Set(highlightedNodes);
    const visibleNodeIds = new Set<string>();

    graphData.nodes.forEach((node) => {
      const isHighlighted = highlightedNodeIds.has(node.id);
      const isInMainComponent = node.data.is_in_largest_component === true;
      const isConnected = (node.data.degree ?? 0) > 0;

      if (
        viewMode === "all" ||
        isHighlighted ||
        (viewMode === "main" && isInMainComponent) ||
        (viewMode === "connected" && isConnected)
      ) {
        visibleNodeIds.add(node.id);
      }
    });

    const visibleEdges = graphData.edges.filter(
      (edge) => visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target)
    );

    return {
      nodes: graphData.nodes.filter((node) => visibleNodeIds.has(node.id)),
      edges: visibleEdges,
    };
  }, [graphData, highlightedNodes, viewMode]);

  const graphMetadata = graphData?.metadata ?? {};
  const hiddenNodeCount = graphData && visibleGraphData
    ? graphData.nodes.length - visibleGraphData.nodes.length
    : 0;
  const visibleEdgeCount = visibleGraphData?.edges.length ?? 0;
  const isolatedNodeCount =
    typeof graphMetadata.isolated_node_count === "number"
      ? graphMetadata.isolated_node_count
      : 0;

  useEffect(() => {
    hasInitializedRef.current = false;
  }, [graphData, viewMode]);

  // Handle fitView - either show full graph or focus on highlighted node
  useEffect(() => {
    if (!isOpen || nodes.length === 0) return;

    // If we have highlighted nodes, focus on them
    if (highlightedNodes.length > 0) {
      const nodeToFocus = nodes.find((n) => n.id === highlightedNodes[0]);
      if (nodeToFocus) {
        // Small delay to ensure container is properly sized
        const timeoutId = setTimeout(() => {
          fitView({
            nodes: [nodeToFocus],
            duration: 800,
            padding: 0.5,
            maxZoom: 1.2,
          });
        }, 150); // Delay for drawer animation

        previousHighlightedRef.current = highlightedNodes;
        return () => clearTimeout(timeoutId);
      }
    } else if (!hasInitializedRef.current) {
      // Initial load - show entire graph with good padding
      const timeoutId = setTimeout(() => {
        fitView({ padding: 0.15, duration: 500, maxZoom: 1.0 });
        hasInitializedRef.current = true;
      }, 150);

      return () => clearTimeout(timeoutId);
    }
  }, [isOpen, highlightedNodes, nodes, fitView]);

  useEffect(() => {
    const handleFullscreenChange = () => {
      const fullscreenElement = document.fullscreenElement;
      const graphIsFullscreen = fullscreenElement === graphContainerRef.current;
      setIsFullscreen(graphIsFullscreen);

      if (graphIsFullscreen) {
        window.setTimeout(() => {
          fitView({ padding: 0.15, duration: 300, maxZoom: 1.0 });
        }, 150);
      }
    };

    document.addEventListener("fullscreenchange", handleFullscreenChange);

    return () => {
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
    };
  }, [fitView]);

  // Update nodes and edges when data changes or the graph filter changes
  useEffect(() => {
    if (visibleGraphData) {
      const readablePositions = createReadableLayout(visibleGraphData);

      // Transform API data to React Flow format
      const flowNodes: Node[] = visibleGraphData.nodes.map((node) => {
        const isHighlighted = highlightedNodes.includes(node.id);
        const entityType = node.data.type || "unknown";

        return {
          id: node.id,
          type: "default",
          position: readablePositions.get(node.id) ?? node.position,
          data: {
            ...node.data,
            label: node.data.label,
            type: entityType,
          },
          style: {
            background: getNodeColor(entityType, isHighlighted),
            color: graphColor("--graph-node-text"),
            border: `3px solid ${getBorderColor(entityType, isHighlighted)}`,
            borderRadius: "8px",
            padding: "12px 16px",
            fontSize: "14px",
            fontWeight: isHighlighted ? "700" : "600",
            minWidth: "120px",
            textAlign: "center",
            boxShadow: isHighlighted
              ? "0 8px 20px rgba(0, 0, 0, 0.22)"
              : "0 2px 8px rgba(0, 0, 0, 0.15)",
            cursor: "pointer",
            transition: "all 0.2s ease",
          },
        };
      });

      const flowEdges: Edge[] = visibleGraphData.edges.map((edge) => {
        const isHighlighted =
          highlightedNodes.includes(edge.source) ||
          highlightedNodes.includes(edge.target);

        // Show label for edges connected to selected node
        const hasLabel = isHighlighted && edge.label;
        const shortLabel = hasLabel
          ? edge.label!.length > 30
            ? edge.label!.substring(0, 27) + "..."
            : edge.label
          : undefined;

        return {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: shortLabel,
          type: hasLabel ? "custom" : "smoothstep",
          animated: isHighlighted,
          data: {
            fullLabel: edge.label,
            isHighlighted,
          },
          style: {
            stroke: isHighlighted
              ? graphColor("--graph-edge-highlight")
              : graphColor("--graph-edge"),
            strokeWidth: isHighlighted ? 3 : 1.5,
            opacity: isHighlighted ? 1 : 0.6,
          },
        };
      });

      setNodes(flowNodes);
      setEdges(flowEdges);
    }
  }, [visibleGraphData, highlightedNodes, setNodes, setEdges]);

  const onNodeClick: NodeMouseHandler = useCallback(
    (_event, node) => {
      onNodeSelect?.(node.id);
    },
    [onNodeSelect]
  );

  const onPaneClick = useCallback(() => {
    onNodeSelect?.(null);
  }, [onNodeSelect]);

  const toggleFullscreen = useCallback(async () => {
    const graphContainer = graphContainerRef.current;
    if (!graphContainer) return;

    if (document.fullscreenElement === graphContainer) {
      await document.exitFullscreen();
      return;
    }

    await graphContainer.requestFullscreen();
  }, []);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center rounded-xl border border-border/60 bg-card">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex h-full flex-col items-center justify-center rounded-xl border border-border/60 bg-card text-muted-foreground">
        <Network className="mb-4 h-16 w-16 text-primary opacity-70" />
        <p className="text-lg font-semibold text-foreground">
          Failed to load graph data
        </p>
        <p className="mt-1 text-sm">Please try refreshing the page</p>
      </div>
    );
  }

  if (!graphData || !visibleGraphData || visibleGraphData.nodes.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center rounded-xl border border-dashed border-border/60 bg-card text-muted-foreground">
        <Network className="mb-4 h-16 w-16 text-primary opacity-70" />
        <p className="text-lg font-semibold text-foreground">
          No graph data available
        </p>
        <p className="mt-1 text-sm">
          Upload a document to build the knowledge graph
        </p>
      </div>
    );
  }

  return (
    <div
      ref={graphContainerRef}
      className={`relative h-full w-full overflow-hidden border border-border ${
        isFullscreen ? "rounded-none" : "rounded-xl"
      }`}
      style={{ background: graphColor("--graph-surface") }}
    >
      <button
        type="button"
        onClick={toggleFullscreen}
        className="absolute right-4 top-4 z-20 inline-flex h-10 w-10 items-center justify-center rounded-lg border border-border/70 bg-card/95 text-foreground shadow-[0_10px_24px_rgba(0,0,0,0.18)] transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        aria-label={isFullscreen ? "Exit graph fullscreen" : "Open graph fullscreen"}
        title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
      >
        {isFullscreen ? (
          <Minimize2 className="h-4 w-4" />
        ) : (
          <Maximize2 className="h-4 w-4" />
        )}
      </button>
      <div className="absolute left-4 top-4 z-20 flex max-w-[calc(100%-7rem)] flex-wrap items-center gap-2">
        <div className="inline-flex overflow-hidden rounded-lg border border-border/70 bg-card/95 shadow-[0_10px_24px_rgba(0,0,0,0.18)]">
          {[
            { id: "main", label: "Main", icon: Network },
            { id: "connected", label: "Connected", icon: GitBranch },
            { id: "all", label: "All", icon: Eye },
          ].map((item) => {
            const Icon = item.icon;
            const active = viewMode === item.id;

            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setViewMode(item.id as GraphViewMode)}
                className={`inline-flex h-10 items-center gap-1.5 px-3 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                  active
                    ? "bg-primary text-primary-foreground"
                    : "text-foreground hover:bg-muted"
                }`}
                aria-pressed={active}
              >
                <Icon className="h-3.5 w-3.5" />
                {item.label}
              </button>
            );
          })}
        </div>
        <div className="inline-flex h-10 items-center gap-2 rounded-lg border border-border/70 bg-card/95 px-3 text-xs font-medium text-muted-foreground shadow-[0_10px_24px_rgba(0,0,0,0.18)]">
          <span>{visibleGraphData.nodes.length} nodes</span>
          <span className="text-border">/</span>
          <span>{visibleEdgeCount} edges</span>
          {hiddenNodeCount > 0 && (
            <>
              <span className="text-border">/</span>
              <span>
                {hiddenNodeCount} hidden
                {isolatedNodeCount > 0 ? `, ${isolatedNodeCount} isolated` : ""}
              </span>
            </>
          )}
        </div>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        edgeTypes={edgeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        minZoom={0.1}
        maxZoom={2}
        defaultEdgeOptions={{
          type: "smoothstep",
          style: { stroke: graphColor("--graph-edge"), strokeWidth: 2.5 },
          animated: false,
        }}
        style={{ background: graphColor("--graph-surface") }}
      >
        <Background color={graphColor("--graph-grid")} gap={18} size={2} />
        <Controls
          style={{
            background: "hsl(var(--card))",
            border: "2px solid hsl(var(--border))",
            borderRadius: "8px",
            boxShadow: "0 4px 12px rgba(0, 0, 0, 0.25)",
          }}
        />
        <MiniMap
          nodeColor={(node) =>
            highlightedNodes.includes(node.id)
              ? graphColor("--graph-edge-highlight")
              : graphColor("--graph-node-person")
          }
          nodeStrokeWidth={3}
          nodeStrokeColor={graphColor("--graph-edge")}
          nodeBorderRadius={4}
          zoomable
          pannable
          maskColor="rgba(0, 0, 0, 0.48)"
          style={{
            background: graphColor("--graph-surface"),
            border: `2px solid ${graphColor("--border")}`,
            borderRadius: "8px",
            boxShadow: "0 4px 12px rgba(0, 0, 0, 0.4)",
            width: 180,
            height: 120,
          }}
        />
      </ReactFlow>
    </div>
  );
}

// Wrap with ReactFlowProvider to enable useReactFlow hook
export function GraphVisualization(props: GraphVisualizationProps) {
  return (
    <ReactFlowProvider>
      <GraphVisualizationInner {...props} />
    </ReactFlowProvider>
  );
}
