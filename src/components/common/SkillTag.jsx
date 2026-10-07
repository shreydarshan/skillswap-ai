import React from 'react';

export default function SkillTag({
  name,
  variant = 'offer',
  size = 'md',
  badge = null,
  icon: Icon = null,
  onClick = null,
  className = ''
}) {
  const baseStyles = 'inline-flex items-center font-medium rounded-full border transition-all duration-150';

  const variants = {
    offer: 'bg-blue-50 text-blue-700 border-blue-200/80 hover:bg-blue-100/80',
    want: 'bg-emerald-50 text-emerald-700 border-emerald-200/80 hover:bg-emerald-100/80',
    category: 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200/70',
    active: 'bg-blue-600 text-white border-blue-600 shadow-xs shadow-blue-500/20',
    neutral: 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
  };

  const sizes = {
    sm: 'px-2.5 py-0.5 text-xs gap-1',
    md: 'px-3 py-1 text-xs sm:text-sm gap-1.5',
    lg: 'px-4 py-1.5 text-sm gap-2'
  };

  const clickable = onClick ? 'cursor-pointer active:scale-95' : '';

  return (
    <span
      onClick={onClick}
      className={`${baseStyles} ${variants[variant] || variants.offer} ${sizes[size] || sizes.md} ${clickable} ${className}`}
    >
      {Icon && <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />}
      <span>{name}</span>
      {badge && (
        <span className="ml-0.5 px-1.5 py-0.2 bg-white/70 text-slate-700 rounded-full text-[10px] font-semibold border border-slate-200/50">
          {badge}
        </span>
      )}
    </span>
  );
}
