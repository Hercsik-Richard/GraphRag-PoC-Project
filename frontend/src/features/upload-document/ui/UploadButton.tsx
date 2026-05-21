/**
 * UploadButton component - File upload for document indexing
 */
import { useEffect, useRef, useState } from "react";
import { Upload, CheckCircle, XCircle } from "lucide-react";
import { cn, FILE_UPLOAD, type ModelProvider } from "@/shared";
import { getIndexProgress, useUploadDocument } from "../api/uploadDocument";

interface UploadButtonProps {
  onUploadComplete?: (graphId: string) => void;
  indexChatProvider: ModelProvider;
  indexEmbedProvider: ModelProvider;
}

export function UploadButton({
  onUploadComplete,
  indexChatProvider,
  indexEmbedProvider,
}: UploadButtonProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { uploadDocument, isUploading, error } = useUploadDocument();
  const [status, setStatus] = useState<"idle" | "indexing" | "success" | "error">("idle");
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");
  const [chunksProcessed, setChunksProcessed] = useState<number | null>(null);
  const [totalChunks, setTotalChunks] = useState<number | null>(null);
  const [currentChunk, setCurrentChunk] = useState<number | null>(null);
  const [currentChunkProgress, setCurrentChunkProgress] = useState<number | null>(null);
  const [phase, setPhase] = useState<string | null>(null);
  const [phaseProcessed, setPhaseProcessed] = useState<number | null>(null);
  const [phaseTotal, setPhaseTotal] = useState<number | null>(null);
  const [phaseProgress, setPhaseProgress] = useState<number | null>(null);
  const [pollingDocumentId, setPollingDocumentId] = useState<string | null>(null);
  const shouldShowProgress = status === "indexing";

  useEffect(() => {
    if (!pollingDocumentId || status !== "indexing") return;

    let cancelled = false;

    const pollProgress = async () => {
      try {
        const current = await getIndexProgress(pollingDocumentId);
        if (cancelled) return;

        setProgress(current.progress);
        setMessage(current.message);
        setChunksProcessed(current.chunks_processed);
        setTotalChunks(current.total_chunks);
        setCurrentChunk(current.current_chunk);
        setCurrentChunkProgress(current.current_chunk_progress);
        setPhase(current.phase);
        setPhaseProcessed(current.phase_processed);
        setPhaseTotal(current.phase_total);
        setPhaseProgress(current.phase_progress);

        if (current.status === "completed") {
          setStatus("success");
          setPollingDocumentId(null);
          onUploadComplete?.(current.graph_id);

          setTimeout(() => {
            setStatus("idle");
            setProgress(0);
            setMessage("");
            setChunksProcessed(null);
            setTotalChunks(null);
            setCurrentChunk(null);
            setCurrentChunkProgress(null);
            setPhase(null);
            setPhaseProcessed(null);
            setPhaseTotal(null);
            setPhaseProgress(null);
            if (fileInputRef.current) {
              fileInputRef.current.value = "";
            }
          }, 4000);
        }

        if (current.status === "failed") {
          setStatus("error");
          setPollingDocumentId(null);
          setMessage(current.error || current.message);

          setTimeout(() => setStatus("idle"), 20000);
        }
      } catch {
        if (!cancelled) {
          setStatus("error");
          setPollingDocumentId(null);
          setMessage("Failed to read indexing progress");
          setTimeout(() => setStatus("idle"), 20000);
        }
      }
    };

    pollProgress();
    const intervalId = window.setInterval(pollProgress, 2000);

    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, [pollingDocumentId, status, onUploadComplete]);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size
    if (file.size > FILE_UPLOAD.MAX_SIZE) {
      setStatus("error");
      setMessage(`File is larger than ${FILE_UPLOAD.MAX_SIZE_MB}MB`);
      setTimeout(() => setStatus("idle"), 3000);
      return;
    }

    try {
      setStatus("indexing");
      setProgress(0);
      setMessage("Uploading document");
      setChunksProcessed(null);
      setTotalChunks(null);
      setCurrentChunk(null);
      setCurrentChunkProgress(null);
      setPhase("Uploading document");
      setPhaseProcessed(null);
      setPhaseTotal(null);
      setPhaseProgress(null);

      const response = await uploadDocument({
        file,
        indexChatProvider,
        indexEmbedProvider,
      });
      setProgress(response.progress);
      setMessage(response.message);
      setPollingDocumentId(response.document_id);
    } catch {
      setStatus("error");
      setMessage("Failed to upload. Please try again.");
      setTimeout(() => setStatus("idle"), 3000);
    }
  };

  const getButtonContent = () => {
    if (isUploading || status === "indexing") {
      return (
        <>
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
          <span className="text-sm">
            {totalChunks !== null && currentChunk !== null && currentChunkProgress !== null
              ? `Chunk ${currentChunk}/${totalChunks} ${currentChunkProgress}%`
              : `Indexing ${progress}%`}
          </span>
        </>
      );
    }

    if (status === "success") {
      return (
        <>
          <CheckCircle className="h-4 w-4" />
          <span className="text-sm">Success!</span>
        </>
      );
    }

    if (status === "error" || error) {
      return (
        <>
          <XCircle className="h-4 w-4" />
          <span className="text-sm">Error</span>
        </>
      );
    }

    return (
      <>
        <Upload className="h-4 w-4" />
        <span className="text-sm">Upload Document</span>
      </>
    );
  };

  return (
    <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
      <input
        ref={fileInputRef}
        type="file"
        accept={FILE_UPLOAD.ACCEPTED_TYPES.join(",")}
        onChange={handleFileChange}
        disabled={isUploading || status === "indexing"}
        className="hidden"
        id="file-upload"
      />
      <label
        htmlFor="file-upload"
        className={cn(
          "inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium",
          "cursor-pointer transition-colors",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
          status === "success" && "bg-success text-success-foreground",
          (status === "error" || error) &&
            "bg-destructive text-destructive-foreground",
          status === "idle" &&
            !error &&
            "bg-secondary text-secondary-foreground hover:bg-secondary/80",
          (isUploading || status === "indexing") && "cursor-not-allowed opacity-70"
        )}
      >
        {getButtonContent()}
      </label>
      {shouldShowProgress && (
        <IndexingProgressPanel
          progress={progress}
          message={message}
          chunksProcessed={chunksProcessed}
          totalChunks={totalChunks}
          currentChunk={currentChunk}
          currentChunkProgress={currentChunkProgress}
          phase={phase}
          phaseProcessed={phaseProcessed}
          phaseTotal={phaseTotal}
          phaseProgress={phaseProgress}
        />
      )}
    </div>
  );
}

function IndexingProgressPanel({
  progress,
  message,
  chunksProcessed,
  totalChunks,
  currentChunk,
  currentChunkProgress,
  phase,
  phaseProcessed,
  phaseTotal,
  phaseProgress,
}: {
  progress: number;
  message: string;
  chunksProcessed: number | null;
  totalChunks: number | null;
  currentChunk: number | null;
  currentChunkProgress: number | null;
  phase: string | null;
  phaseProcessed: number | null;
  phaseTotal: number | null;
  phaseProgress: number | null;
}) {
  const hasChunkProgress = chunksProcessed !== null && totalChunks !== null;
  const hasCurrentChunkProgress =
    currentChunk !== null && currentChunkProgress !== null && totalChunks !== null;
  const hasPhaseProgress =
    phaseProcessed !== null && phaseTotal !== null && phaseProgress !== null;

  return (
    <div className="w-full min-w-[18rem] max-w-md rounded-lg border border-border/70 bg-background/80 px-3 py-2 shadow-sm sm:w-96">
      <div className="mb-2 flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
            Indexing status
          </p>
          <p className="mt-0.5 truncate text-xs font-semibold text-foreground">
            {phase || message || "Indexing document"}
          </p>
        </div>
        <span className="shrink-0 text-sm font-bold text-accent">{progress}%</span>
      </div>

      <div className="space-y-2">
        <ProgressMeter label="Overall" value={progress} tone="accent" />

        {hasPhaseProgress && (
          <ProgressMeter
            label={`${phaseProcessed} / ${phaseTotal}`}
            value={phaseProgress}
            tone="primary"
          />
        )}

        {hasCurrentChunkProgress && (
          <ProgressMeter
            label={`Current chunk ${currentChunk} / ${totalChunks}`}
            value={currentChunkProgress}
            tone="secondary"
          />
        )}

        <div className="flex flex-wrap items-center justify-between gap-2 text-[0.7rem] text-muted-foreground">
          <span className="truncate">{message}</span>
          {hasChunkProgress && (
            <span className="shrink-0 font-medium text-foreground">
              Chunks {chunksProcessed} / {totalChunks}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

function ProgressMeter({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: "accent" | "primary" | "secondary";
}) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between gap-3 text-[0.68rem]">
        <span className="truncate text-muted-foreground">{label}</span>
        <span className="font-medium text-foreground">{value}%</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-muted">
        <div
          className={cn(
            "h-full transition-all duration-500",
            tone === "accent" && "bg-accent",
            tone === "primary" && "bg-primary",
            tone === "secondary" && "bg-secondary"
          )}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}
