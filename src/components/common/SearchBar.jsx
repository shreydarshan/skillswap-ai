import React, { forwardRef } from 'react';
import { Search, X } from 'lucide-react';

const SearchBar = forwardRef(function SearchBar(
  {
    value = '',
    onChange,
    onSubmit = null,
    onEscape = null,
    onFocus = null,
    onBlur = null,
    placeholder = 'Search skills, topics, or student names...',
    className = '',
    autoFocus = false,
    onClear = null,
    showShortcut = true,
  },
  ref
) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      if (onSubmit) onSubmit(value);
    } else if (e.key === 'Escape') {
      if (onEscape) onEscape();
      e.target.blur();
    }
  };

  return (
    <div className={`relative flex items-center w-full ${className}`}>
      <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
      <input
        ref={ref}
        type="text"
        value={value}
        onChange={(e) => onChange && onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={onFocus}
        onBlur={onBlur}
        placeholder={placeholder}
        autoFocus={autoFocus}
        className="w-full pl-10 pr-10 py-2.5 bg-white text-slate-900 placeholder:text-slate-400 border border-slate-200/90 rounded-xl text-sm focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 shadow-2xs transition-all duration-200"
      />
      {value ? (
        <button
          type="button"
          onClick={() => {
            if (onClear) onClear();
            else if (onChange) onChange('');
          }}
          className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-600 rounded-md hover:bg-slate-100 transition-colors cursor-pointer"
          aria-label="Clear search"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      ) : showShortcut ? (
        <div className="hidden sm:flex items-center absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none">
          <kbd className="px-1.5 py-0.5 text-[10px] font-mono font-medium text-slate-400 bg-slate-100 border border-slate-200/80 rounded shadow-2xs">
            /
          </kbd>
        </div>
      ) : null}
    </div>
  );
});

export default SearchBar;
