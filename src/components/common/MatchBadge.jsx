import React from 'react';
import { Sparkles } from 'lucide-react';

export default function MatchBadge({ percentage = 95, label = 'Match', showLabel = true, size = 'md', className = '' }) {
  let colorStyle = 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-xs shadow-blue-500/20';
  if (percentage < 85) {
    colorStyle = 'bg-blue-50 text-blue-700 border border-blue-200';
  } else if (percentage < 92) {
    colorStyle = 'bg-emerald-50 text-emerald-700 border border-emerald-200';
  }

  const sizes = {
    sm: 'px-2 py-0.5 text-xs gap-1',
    md: 'px-2.5 py-1 text-xs font-semibold gap-1.5',
    lg: 'px-3 py-1.5 text-sm font-bold gap-2'
  };

  return (
    <span
      className={`inline-flex items-center rounded-full transition-all duration-200 ${colorStyle} ${sizes[size] || sizes.md} ${className}`}
      title="SkillSwap AI Recommendation Compatibility Score"
    >
      <Sparkles className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5 animate-pulse'} />
      <span>{percentage}% {showLabel ? label : ''}</span>
    </span>
  );
}
