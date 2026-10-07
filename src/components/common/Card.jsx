import React from 'react';

export default function Card({
  children,
  className = '',
  hoverEffect = false,
  padding = 'normal',
  onClick = null,
  ...props
}) {
  const paddingStyles = {
    none: 'p-0',
    tight: 'p-3 sm:p-4',
    normal: 'p-4 sm:p-6',
    spacious: 'p-6 sm:p-8'
  };

  const hoverStyle = hoverEffect
    ? 'transition-all duration-200 hover:shadow-md hover:border-slate-300 hover:-translate-y-0.5 cursor-pointer'
    : '';

  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-2xl border border-slate-200/80 shadow-xs ${paddingStyles[padding] || paddingStyles.normal} ${hoverStyle} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
