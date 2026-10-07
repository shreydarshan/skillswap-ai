import React, { useState } from 'react';
import { getAvatarUrl, getInitials, getInitialsBg, getAvatarObjectPosition } from '../../utils/avatar';

const SIZE_MAP = {
  xs: 'w-7 h-7 text-[10px] rounded-lg',
  sm: 'w-9 h-9 text-xs rounded-xl',
  md: 'w-12 h-12 text-sm rounded-2xl',
  lg: 'w-14 h-14 sm:w-16 sm:h-16 text-base rounded-2xl',
  xl: 'w-20 h-20 text-xl rounded-3xl',
  '2xl': 'w-28 h-28 sm:w-32 sm:h-32 text-2xl sm:text-3xl rounded-3xl',
};

const STATUS_SIZE_MAP = {
  xs: 'w-2 h-2 -bottom-0.5 -right-0.5 ring-1.5',
  sm: 'w-2.5 h-2.5 -bottom-0.5 -right-0.5 ring-2',
  md: 'w-3 h-3 -bottom-0.5 -right-0.5 ring-2',
  lg: 'w-3.5 h-3.5 -bottom-0.5 -right-0.5 ring-2.5',
  xl: 'w-4 h-4 -bottom-1 -right-1 ring-3',
  '2xl': 'w-5 h-5 -bottom-1 -right-1 ring-3',
};

export default function ProfileAvatar({
  src = null,
  name = '',
  email = '',
  genderPreference = '',
  size = 'md',
  className = '',
  statusIndicator = false,
  statusColor = 'bg-emerald-500',
  alt = '',
  objectPosition = null,
  onClick = null,
}) {
  const [imgFailed, setImgFailed] = useState(false);

  const resolvedUrl = !imgFailed ? getAvatarUrl(src, name, email, genderPreference) : null;
  const sizeClasses = SIZE_MAP[size] || SIZE_MAP.md;
  const statusSize = STATUS_SIZE_MAP[size] || STATUS_SIZE_MAP.md;
  const initials = getInitials(name, email);
  const initialsGradient = getInitialsBg(name, email);
  const resolvedObjectPosition = objectPosition || getAvatarObjectPosition(resolvedUrl);

  const isClickable = typeof onClick === 'function';

  return (
    <div
      onClick={onClick}
      className={`relative inline-flex shrink-0 select-none ${isClickable ? 'cursor-pointer hover:opacity-90 transition-opacity' : ''} ${className}`}
    >
      {/* Universal Fixed 1:1 Aspect-Ratio Frame */}
      <div className={`${sizeClasses} aspect-square overflow-hidden shrink-0 flex items-center justify-center bg-slate-100`}>
        {resolvedUrl && !imgFailed ? (
          <img
            src={resolvedUrl}
            alt={alt || name || 'Student Profile'}
            onError={() => setImgFailed(true)}
            style={{
              objectPosition: resolvedObjectPosition,
            }}
            className="w-full h-full object-cover aspect-square select-none block"
            loading="lazy"
          />
        ) : (
          /* Deterministic Initials Avatar Fallback */
          <div
            className={`w-full h-full bg-gradient-to-br ${initialsGradient} text-white font-bold flex items-center justify-center select-none tracking-wider`}
          >
            {initials}
          </div>
        )}
      </div>

      {/* Optional Online Status Indicator */}
      {statusIndicator && (
        <span
          className={`absolute ${statusSize} ${statusColor} rounded-full ring-white ring-offset-0`}
        />
      )}
    </div>
  );
}
