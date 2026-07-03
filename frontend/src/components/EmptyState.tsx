import React from 'react';
import { Inbox } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  message?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No data available',
  message = 'There is no data to display at this time.',
  icon,
  action,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      <div className="w-16 h-16 rounded-2xl bg-[rgba(148,163,184,0.08)] border border-[rgba(148,163,184,0.12)] flex items-center justify-center mb-6">
        {icon || <Inbox className="w-8 h-8 text-[#64748b]" />}
      </div>
      <h3 className="text-lg font-semibold text-[#f1f5f9] mb-2">{title}</h3>
      <p className="text-sm text-[#94a3b8] max-w-md mb-6">{message}</p>
      {action}
    </div>
  );
};
