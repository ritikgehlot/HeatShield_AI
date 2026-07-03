import React, { useCallback, useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, XCircle, Loader2 } from 'lucide-react';

interface FileUploadProps {
  accept: string;
  label: string;
  description: string;
  onUpload: (file: File) => void;
  isUploading?: boolean;
  uploadResult?: { success: boolean; message: string } | null;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  accept,
  label,
  description,
  onUpload,
  isUploading = false,
  uploadResult = null,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) {
        setSelectedFile(file);
        onUpload(file);
      }
    },
    [onUpload]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        setSelectedFile(file);
        onUpload(file);
      }
    },
    [onUpload]
  );

  return (
    <div className="glass-card p-5">
      <h3 className="text-sm font-semibold text-[#f1f5f9] mb-1">{label}</h3>
      <p className="text-xs text-[#94a3b8] mb-4">{description}</p>

      {/* Drop Zone */}
      <div
        className={`relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
          isDragging
            ? 'border-[#f97316] bg-[rgba(249,115,22,0.05)]'
            : 'border-[rgba(148,163,184,0.15)] hover:border-[rgba(148,163,184,0.3)] hover:bg-[rgba(148,163,184,0.03)]'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleFileSelect}
          className="hidden"
          aria-label={label}
        />

        {isUploading ? (
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="w-8 h-8 text-[#f97316] animate-spin" />
            <p className="text-sm text-[#94a3b8]">Uploading...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <Upload className="w-8 h-8 text-[#64748b]" />
            <div>
              <p className="text-sm text-[#f1f5f9] font-medium">
                Drop file here or <span className="text-[#f97316]">browse</span>
              </p>
              <p className="text-xs text-[#64748b] mt-1">Accepts {accept} files</p>
            </div>
          </div>
        )}
      </div>

      {/* Selected File */}
      {selectedFile && !isUploading && (
        <div className="flex items-center gap-2 mt-3 text-xs text-[#94a3b8]">
          <FileText className="w-3.5 h-3.5" />
          <span>{selectedFile.name}</span>
          <span className="text-[#64748b]">({(selectedFile.size / 1024).toFixed(1)} KB)</span>
        </div>
      )}

      {/* Upload Result */}
      {uploadResult && (
        <div
          className={`flex items-center gap-2 mt-3 p-3 rounded-lg text-xs ${
            uploadResult.success
              ? 'bg-[rgba(34,197,94,0.1)] text-[#4ade80]'
              : 'bg-[rgba(239,68,68,0.1)] text-[#f87171]'
          }`}
        >
          {uploadResult.success ? (
            <CheckCircle className="w-4 h-4 flex-shrink-0" />
          ) : (
            <XCircle className="w-4 h-4 flex-shrink-0" />
          )}
          <span>{uploadResult.message}</span>
        </div>
      )}
    </div>
  );
};
