/**
 * UploadButton component - File upload for document indexing
 */
import { useEffect, useRef, useState } from "react";
import { Upload, CheckCircle, XCircle } from "lucide-react";
import { cn, FILE_UPLOAD, type ModelProvider } from "@/shared";
import { getIndexProgress, useUploadDocument } from "../api/uploadDocument";

interface UploadButtonProps {
  onUploadComplete?: () => void;
  modelProvider: ModelProvider;
}

export function UploadButton({ onUploadComplete, modelProvider }: UploadButtonProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { uploadDocument, isUploading, error } = useUploadDocument();
  const [status, setStatus] = useState<"idle" | "indexing" | "success" | "error">("idle");
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");
  const [chunksProcessed, setChunksProcessed] = useState<number | null>(null);
  const [totalChunks, setTotalChunks] = useState<number | null>(null);
  const [currentChunk, setCurrentChunk] = useState<number | null>(null);
  const [currentChunkProgress, setCurrentChunkProgress] = useState<number | null>(null);
  const [pollingDocumentId, setPollingDocumentId] = useState<string | null>(null);
  const shouldShowProgress = status === "indexing" || status === "success" || status === "error";

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

        if (current.status === "completed") {
          setStatus("success");
          setPollingDocumentId(null);
          onUploadComplete?.();

          setTimeout(() => {
            setStatus("idle");
            setProgress(0);
            setMessage("");
            setChunksProcessed(null);
            setTotalChunks(null);
            setCurrentChunk(null);
            setCurrentChunkProgress(null);
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

      const response = await uploadDocument({ file, modelProvider });
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
    <div>
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
        <>
          <IndexingProgressBar
            status={status}
            progress={progress}
            message={message}
            error={error}
            chunksProcessed={chunksProcessed}
            totalChunks={totalChunks}
            currentChunk={currentChunk}
            currentChunkProgress={currentChunkProgress}
          />
          <div className="fixed bottom-6 right-6 z-50 w-80 max-w-[calc(100vw-3rem)] rounded-xl border border-border/60 bg-card p-4 shadow-[0_20px_42px_rgba(0,0,0,0.22)]">
            <div className="mb-3 flex items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                  Index status
                </p>
                <p className="mt-1 truncate text-sm font-semibold text-foreground">
                  {status === "success"
                    ? "Completed"
                    : status === "error"
                      ? "Failed"
                      : "Indexing document"}
                </p>
              </div>
              <span className="shrink-0 text-sm font-bold text-accent">{progress}%</span>
            </div>
            <IndexingProgressBar
              status={status}
              progress={progress}
              message={message}
              error={error}
              chunksProcessed={chunksProcessed}
              totalChunks={totalChunks}
              currentChunk={currentChunk}
              currentChunkProgress={currentChunkProgress}
            />
          </div>
        </>
      )}
    </div>
  );
}

function IndexingProgressBar({
  status,
  progress,
  message,
  error,
  chunksProcessed,
  totalChunks,
  currentChunk,
  currentChunkProgress,
}: {
  status: "idle" | "indexing" | "success" | "error";
  progress: number;
  message: string;
  error: unknown;
  chunksProcessed: number | null;
  totalChunks: number | null;
  currentChunk: number | null;
  currentChunkProgress: number | null;
}) {
  const hasChunkProgress = chunksProcessed !== null && totalChunks !== null;
  const hasCurrentChunkProgress =
    currentChunk !== null && currentChunkProgress !== null && totalChunks !== null;

  return (
    <div className="mt-2 w-64 max-w-full space-y-2">
      <div>
        <div className="mb-1 flex items-center justify-between gap-3 text-xs">
          <span className="text-muted-foreground">Overall</span>
          <span className="font-medium text-foreground">{progress}%</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-background/60">
          <div
            className={cn(
              "h-full transition-all duration-500",
              status === "error" ? "bg-destructive" : "bg-accent"
            )}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {hasCurrentChunkProgress && (
        <div>
          <div className="mb-1 flex items-center justify-between gap-3 text-xs">
            <span className="text-muted-foreground">
              Current chunk {currentChunk} / {totalChunks}
            </span>
            <span className="font-medium text-foreground">{currentChunkProgress}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-background/60">
            <div
              className={cn(
                "h-full transition-all duration-500",
                status === "error" ? "bg-destructive" : "bg-secondary"
              )}
              style={{ width: `${currentChunkProgress}%` }}
            />
          </div>
        </div>
      )}

      {hasChunkProgress && (
        <p className="text-xs font-medium text-foreground">
          Completed chunks: {chunksProcessed} / {totalChunks}
        </p>
      )}

      <p
        className={cn(
          "text-xs",
          status === "error" ? "text-destructive" : "text-muted-foreground"
        )}
      >
        {message || (error ? "Failed to upload. Please try again." : "")}
      </p>
    </div>
  );
}
