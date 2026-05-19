/**
 * MessageCitations component - Displays compact footnotes/citations with tooltips
 */
import type {
  RetrievedEntity,
  RetrievedRelationship,
} from "@/entities/message";

interface MessageCitationsProps {
  entities?: RetrievedEntity[];
  relationships?: RetrievedRelationship[];
  onEntityClick?: (entityId: string) => void;
  onRelationshipClick?: (source: string, target: string) => void;
}

export function MessageCitations({
  entities = [],
  relationships = [],
  onEntityClick,
  onRelationshipClick,
}: MessageCitationsProps) {
  if (entities.length === 0 && relationships.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 pt-3 border-t border-border/30 text-xs">
      <div className="font-semibold text-muted-foreground/80 mb-2 text-[10px] uppercase tracking-wider">
        Sources
      </div>

      <div className="flex flex-wrap gap-1.5">
        {/* Entities */}
        {entities.map((entity, idx) => {
          const identifier = entity.title ?? entity.id;
          const displayIndex = entity.index !== undefined ? entity.index : idx;
          const tooltipText = [
            entity.title ?? entity.id,
            entity.type && `Type: ${entity.type}`,
            entity.description,
          ]
            .filter(Boolean)
            .join("\n");

          return (
            <button
              key={entity.id}
              onClick={() => {
                if (identifier) {
                  onEntityClick?.(identifier);
                }
              }}
              title={tooltipText}
              className="inline-flex items-center gap-1 px-2 py-1 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/30 hover:border-primary rounded transition-colors text-[11px] font-medium"
            >
              <span className="font-mono">[{displayIndex}]</span>
              <span>{entity.title ?? entity.id}</span>
            </button>
          );
        })}

        {/* Relationships */}
        {relationships.map((rel, idx) => {
          const displayIndex = rel.index !== undefined ? rel.index : idx;
          const tooltipText = [
            `${rel.source} → ${rel.target}`,
            rel.description,
            rel.weight && `Weight: ${rel.weight}`,
          ]
            .filter(Boolean)
            .join("\n");

          return (
            <button
              key={rel.id}
              onClick={() => {
                onRelationshipClick?.(rel.source, rel.target);
              }}
              title={tooltipText}
              className="inline-flex items-center gap-1 px-2 py-1 bg-secondary/10 hover:bg-secondary/20 text-secondary border border-secondary/30 hover:border-secondary rounded transition-colors text-[11px] font-medium"
            >
              <span className="font-mono">[{displayIndex}]</span>
              <span>{rel.source}</span>
              <span className="opacity-60">→</span>
              <span>{rel.target}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
