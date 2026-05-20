/**
 * MessageCitations component - Displays compact footnotes/citations with tooltips
 */
import type {
  RetrievedEntity,
  RetrievedRelationship,
  RetrievedSource,
} from "@/entities/message";

interface MessageCitationsProps {
  entities?: RetrievedEntity[] | null;
  relationships?: RetrievedRelationship[] | null;
  sources?: RetrievedSource[] | null;
  onEntityClick?: (entityId: string) => void;
  onRelationshipClick?: (source: string, target: string) => void;
}

export function MessageCitations({
  entities,
  relationships,
  sources,
  onEntityClick,
  onRelationshipClick,
}: MessageCitationsProps) {
  const safeEntities = (entities ?? []).slice(0, 8);
  const safeRelationships = (relationships ?? []).slice(0, 8);
  const safeSources = (sources ?? []).slice(0, 8);

  if (
    safeEntities.length === 0 &&
    safeRelationships.length === 0 &&
    safeSources.length === 0
  ) {
    return null;
  }

  return (
    <div className="mt-3 pt-3 border-t border-border/30 text-xs">
      <div className="font-semibold text-muted-foreground/80 mb-2 text-[10px] uppercase tracking-wider">
        Sources
      </div>

      <div className="flex flex-wrap gap-1.5">
        {/* Raw source excerpts */}
        {safeSources.map((source, idx) => {
          const displayIndex = source.id || `S${idx + 1}`;
          const sourceLabel = source.source || `Text unit ${source.text_unit_id}`;
          const tooltipText = [
            sourceLabel,
            source.text_unit_id && `Text unit: ${source.text_unit_id}`,
            source.excerpt,
          ]
            .filter(Boolean)
            .join("\n");

          return (
            <details
              key={`${source.id}-${source.text_unit_id}`}
              title={tooltipText}
              className="group max-w-full"
            >
              <summary className="inline-flex max-w-full cursor-pointer list-none items-center gap-1 rounded border border-amber-500/35 bg-amber-500/10 px-2 py-1 text-[11px] font-medium text-amber-700 transition-colors hover:bg-amber-500/15 dark:text-amber-300 [&::-webkit-details-marker]:hidden">
                <span className="font-mono">[{displayIndex}]</span>
                <span className="truncate">{sourceLabel}</span>
              </summary>
              {source.excerpt ? (
                <div className="mt-1 max-w-[min(36rem,85vw)] rounded border border-amber-500/25 bg-background p-2 text-[11px] leading-relaxed text-foreground shadow-sm">
                  <div className="mb-1 font-mono text-[10px] text-muted-foreground">
                    text unit: {source.text_unit_id}
                  </div>
                  <div className="line-clamp-6">{source.excerpt}</div>
                </div>
              ) : null}
            </details>
          );
        })}

        {/* Entities */}
        {safeEntities.map((entity, idx) => {
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
        {safeRelationships.map((rel, idx) => {
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
