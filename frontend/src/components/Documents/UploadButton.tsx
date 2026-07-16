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
      // Reset so the same file can be re-uploaded if needed
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
        className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg
                   text-sm font-medium transition-all cursor-pointer
                   bg-accent text-white hover:bg-accent-hover
                   disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Upload size={15} />
        {isUploading ? "Uploading..." : "Upload PDF"}
      </button>

      {/* Progress bar */}
      {isUploading && uploadProgress !== null && (
        <div className="mt-2.5">
          <div className="w-full h-1.5 bg-surface-elevated rounded-full overflow-hidden">
            <div
              className="h-full bg-accent rounded-full transition-all duration-300 progress-bar"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <p className="text-xs text-text-muted mt-1 text-center tabular-nums">
            {uploadProgress}%
          </p>
        </div>
      )}

      {/* Error */}
      {uploadError && (
        <p className="text-xs text-error mt-2 text-center">{uploadError}</p>
      )}
    </div>
  );
}
