import { useRef } from "react";
import { Upload } from "lucide-react";

interface UploadButtonProps {
  isUploading: boolean;
  uploadProgress: number | null;
  uploadError: string | null;
  onUpload: (file: File) => void;
}

export default function UploadButton({
  isUploading,
  uploadProgress,
  uploadError,
  onUpload,
}: UploadButtonProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleClick() {
    if (!isUploading) {
      fileInputRef.current?.click();
    }
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file);
      e.target.value = "";
    }
  }

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,application/pdf"
        onChange={handleChange}
        className="hidden"
      />

      <button
        onClick={handleClick}
        disabled={isUploading}
        className="w-full flex items-center justify-center gap-1.5 px-3 py-2 rounded-md
                   text-xs font-medium cursor-pointer premium-btn
                   border border-border hover:border-border-strong
                   bg-surface-elevated text-text-secondary hover:text-text-primary
                   disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <Upload size={12} />
        {isUploading ? "Uploading..." : "Upload PDF"}
      </button>

      {/* Progress */}
      {isUploading && uploadProgress !== null && (
        <div className="mt-2">
          <div className="w-full h-1 bg-surface-active rounded-full overflow-hidden">
            <div
              className="h-full bg-accent rounded-full transition-all duration-300 progress-bar"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <p className="text-[10px] text-text-muted mt-1 text-center tabular-nums">
            {uploadProgress}%
          </p>
        </div>
      )}

      {uploadError && (
        <p className="text-[10px] text-error mt-1.5 text-center">{uploadError}</p>
      )}
    </div>
  );
}
