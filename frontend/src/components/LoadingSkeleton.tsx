import React from 'react';

interface LoadingSkeletonProps {
  className?: string;
  variant?: 'card' | 'text' | 'circle' | 'chart' | 'map';
  count?: number;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  className = '',
  variant = 'card',
  count = 1,
}) => {
  const items = Array.from({ length: count }, (_, i) => i);

  if (variant === 'text') {
    return (
      <div className={`space-y-3 ${className}`}>
        {items.map((i) => (
          <div
            key={i}
            className="h-4 animate-shimmer rounded"
            style={{ width: `${80 - i * 15}%` }}
          />
        ))}
      </div>
    );
  }

  if (variant === 'circle') {
    return (
      <div className={`flex gap-4 ${className}`}>
        {items.map((i) => (
          <div key={i} className="w-12 h-12 rounded-full animate-shimmer" />
        ))}
      </div>
    );
  }

  if (variant === 'chart') {
    return (
      <div className={`glass-card-static p-6 ${className}`}>
        <div className="h-5 w-32 animate-shimmer rounded mb-4" />
        <div className="flex items-end gap-2 h-48">
          {[40, 65, 35, 80, 55, 70, 45].map((h, i) => (
            <div
              key={i}
              className="flex-1 animate-shimmer rounded-t"
              style={{ height: `${h}%` }}
            />
          ))}
        </div>
      </div>
    );
  }

  if (variant === 'map') {
    return (
      <div className={`glass-card-static p-4 ${className}`}>
        <div className="w-full h-full min-h-[400px] animate-shimmer rounded-xl" />
      </div>
    );
  }

  return (
    <div className={`grid gap-4 ${className}`}>
      {items.map((i) => (
        <div key={i} className="glass-card-static p-6 space-y-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl animate-shimmer" />
            <div className="flex-1 space-y-2">
              <div className="h-4 w-24 animate-shimmer rounded" />
              <div className="h-3 w-16 animate-shimmer rounded" />
            </div>
          </div>
          <div className="h-8 w-20 animate-shimmer rounded" />
          <div className="h-3 w-full animate-shimmer rounded" />
        </div>
      ))}
    </div>
  );
};
