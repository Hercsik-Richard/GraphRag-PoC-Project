/**
 * CustomEdge - Edge component with expandable label on hover
 */
import { useState, useCallback, useRef } from "react";
import {
  EdgeLabelRenderer,
  BaseEdge,
  getSmoothStepPath,
  type EdgeProps,
} from "reactflow";

interface CustomEdgeData {
  fullLabel?: string;
  isHighlighted?: boolean;
}

export function CustomEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  style,
  markerEnd,
  label,
}: EdgeProps<CustomEdgeData>) {
  const [isHovered, setIsHovered] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const handleMouseEnter = useCallback(() => {
    setIsHovered(true);
  }, []);

  const handleMouseLeave = useCallback((e: React.MouseEvent) => {
    // Check if we're still within the container bounds
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const { clientX, clientY } = e;
      if (
        clientX >= rect.left &&
        clientX <= rect.right &&
        clientY >= rect.top &&
        clientY <= rect.bottom
      ) {
        return; // Still inside, don't close
      }
    }
    setIsHovered(false);
  }, []);

  const fullLabel = data?.fullLabel;
  const isHighlighted = data?.isHighlighted ?? false;
  const displayLabel = label as string | undefined;

  // Only show label if we have one
  if (!displayLabel && !fullLabel) {
    return (
      <BaseEdge id={id} path={edgePath} style={style} markerEnd={markerEnd} />
    );
  }

  // Check if there's more content to show (label is truncated)
  const showFullLabel = isHovered;

  return (
    <>
      <BaseEdge id={id} path={edgePath} style={style} markerEnd={markerEnd} />
      <EdgeLabelRenderer>
        <div
          ref={containerRef}
          className="nodrag nopan react-flow__edge-label-wrapper"
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          style={{
            position: "absolute",
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: "auto",
            zIndex: showFullLabel ? 10000 : 100,
            isolation: "isolate",
          }}
        >
          {/* Visible label with built-in padding for hit area */}
          <div
            style={{
              position: "relative",
              background: "hsl(var(--card))",
              padding: showFullLabel ? "10px 14px" : "8px 10px",
              borderRadius: showFullLabel ? "8px" : "4px",
              fontSize: showFullLabel ? "13px" : "11px",
              fontWeight: 600,
              color: "hsl(var(--foreground))",
              boxShadow: showFullLabel
                ? "0 8px 24px rgba(0, 0, 0, 0.4)"
                : "0 2px 6px rgba(0, 0, 0, 0.15)",
              border: showFullLabel
                ? "2px solid hsl(var(--graph-edge-highlight))"
                : isHighlighted
                ? "1px solid hsl(var(--graph-edge-highlight))"
                : "1px solid hsl(var(--graph-edge))",
              maxWidth: showFullLabel ? "320px" : "150px",
              whiteSpace: showFullLabel ? "normal" : "nowrap",
              overflow: "hidden",
              textOverflow: showFullLabel ? "clip" : "ellipsis",
              transition: "all 0.15s ease-in-out",
              lineHeight: showFullLabel ? "1.5" : "1.2",
              cursor: showFullLabel ? "pointer" : "default",
            }}
          >
            {showFullLabel ? fullLabel : displayLabel}
          </div>
        </div>
      </EdgeLabelRenderer>
    </>
  );
}
