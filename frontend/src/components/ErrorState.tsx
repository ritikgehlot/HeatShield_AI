import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went wrong',
  message = 'Failed to load data. Please check your connection and try again.',
  onRetry,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      <div className="w-16 h-16 rounded-2xl bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.2)] flex items-center justify-center mb-6">
        <AlertTriangle className="w-8 h-8 text-[#ef4444]" />
      </div>
      <h3 className="text-lg font-semibold text-[#f1f5f9] mb-2">{title}</h3>
      <p className="text-sm text-[#94a3b8] max-w-md mb-6">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[rgba(249,115,22,0.1)] border border-[rgba(249,115,22,0.3)] text-[#f97316] hover:bg-[rgba(249,115,22,0.2)] transition-all text-sm font-medium"
        >
          <RefreshCw className="w-4 h-4" />
          Retry
        </button>
      )}
    </div>
  );
};
