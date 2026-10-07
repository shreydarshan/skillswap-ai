/**
 * Realistic Student Profile Photo Collection & Deterministic Avatar Resolution
 * Stage 9: Eliminates cartoon/emoji avatars and guarantees zero broken-image states.
 */

export const REALISTIC_AVATARS = {
  female: [
    'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80', // Sophia Chen
    'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&auto=format&fit=crop&q=80', // Elena Rostova
    'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&auto=format&fit=crop&q=80', // Sarah Jenkins
    'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400&auto=format&fit=crop&q=80',
  ],
  male: [
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80', // Marcus Vance
    'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80', // Alex Rivera
    'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=400&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&auto=format&fit=crop&q=80',
  ],
  neutral: [
    'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=400&auto=format&fit=crop&q=80',
  ]
};

export const AVATAR_OBJECT_POSITIONS = {
  '1534528741775-53994a69daeb': 'center 20%', // Sophia Chen
  '1517841905240-472988babdf9': 'center 20%', // Elena Rostova
  '1494790108377-be9c29b29330': 'center 25%', // Sarah Jenkins
  '1524504388940-b1c1722653e1': 'center 25%',
  '1544005313-94ddf0286df2': 'center 25%',
  '1531746020798-e6953c6e8e04': 'center 25%',
  '1507003211169-0a1dd7228f2d': 'center 25%', // Marcus Vance
  '1500648767791-00dcc994a43e': 'center 20%', // Alex Rivera
  '1539571696357-5a69c17a67c6': 'center 25%',
  '1506794778202-cad84cf45f1d': 'center 25%',
  '1519085360753-af0119f7cbe7': 'center 25%',
  '1535713875002-d1d0cf377fde': 'center 25%',
  '1570295999919-56ceb5ecca61': 'center 25%',
};

export function getAvatarObjectPosition(url = '') {
  if (!url || typeof url !== 'string') return 'center center';
  for (const [key, pos] of Object.entries(AVATAR_OBJECT_POSITIONS)) {
    if (url.includes(key)) return pos;
  }
  return 'center center';
}

/**
 * Deterministically retrieves realistic photo URL for preference
 */
export function getRealisticPhotoUrl(genderPreference = '', seed = '') {
  const pref = (genderPreference || '').toLowerCase();
  const hash = getHash(seed || 'student');
  if (pref.includes('female')) {
    return REALISTIC_AVATARS.female[hash % REALISTIC_AVATARS.female.length];
  }
  if (pref.includes('male')) {
    return REALISTIC_AVATARS.male[hash % REALISTIC_AVATARS.male.length];
  }
  if (pref.includes('non-binary') || pref.includes('neutral')) {
    return REALISTIC_AVATARS.neutral[hash % REALISTIC_AVATARS.neutral.length];
  }
  return null;
}

/**
 * Calculates deterministic integer from seed string
 */
function getHash(str = '') {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  return Math.abs(hash);
}

/**
 * Generates initials from name or email
 * "Shrey Darshan" -> "SD", "Raghuraj" -> "R"
 */
export function getInitials(name = '', email = '') {
  const cleanName = (name || '').trim();
  if (cleanName) {
    const parts = cleanName.split(/\s+/).filter(Boolean);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return cleanName.slice(0, 2).toUpperCase();
  }

  const cleanEmail = (email || '').trim();
  if (cleanEmail) {
    const userPart = cleanEmail.split('@')[0];
    const parts = userPart.split(/[._-]/).filter(Boolean);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return userPart.slice(0, 2).toUpperCase();
  }

  return 'U';
}

/**
 * Returns deterministic background gradient/color for initials
 */
export function getInitialsBg(name = '', email = '') {
  const seed = (name || email || 'student').trim();
  const hash = getHash(seed);
  const gradients = [
    'from-blue-600 to-indigo-700',
    'from-indigo-600 to-purple-700',
    'from-blue-700 to-cyan-600',
    'from-emerald-600 to-teal-700',
    'from-violet-600 to-indigo-800',
    'from-slate-700 to-slate-900',
  ];
  return gradients[hash % gradients.length];
}

/**
 * Generates clean deterministic SVG data URI for initials avatar
 */
export function getInitialsSvgUrl(name = '', email = '') {
  const initials = getInitials(name, email);
  const seed = (name || email || 'student').trim();
  const hash = getHash(seed);
  const colors = ['#2563eb', '#4f46e5', '#0891b2', '#0d9488', '#7c3aed', '#1e293b'];
  const bgColor = colors[hash % colors.length];

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
      <rect width="128" height="128" rx="36" fill="${bgColor}"/>
      <text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="48" font-weight="700" letter-spacing="1">${initials}</text>
    </svg>
  `.trim();

  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

/**
 * Resolves avatar URL with realistic student portraits and initials fallback.
 * - Explicit Unsplash/photo URL takes priority.
 * - Cartoon/Dicebear URLs are replaced with realistic portraits or initials.
 * - When preference is specified, picks a realistic portrait.
 * - Real users without a photo style get clean initials avatar.
 */
export function getAvatarUrl(avatarUrl, name = '', email = '', genderPreference = '') {
  // If a valid custom photo URL is passed (excluding legacy Dicebear cartoons)
  if (avatarUrl && typeof avatarUrl === 'string' && avatarUrl.trim() !== '') {
    const trimmed = avatarUrl.trim();
    if (!trimmed.includes('dicebear.com')) {
      return trimmed;
    }
  }

  const seed = (name || email || 'student').trim();
  const pref = (genderPreference || '').toLowerCase();

  // If user explicitly picked realistic portrait styles
  if (pref.includes('female')) {
    const idx = getHash(seed) % REALISTIC_AVATARS.female.length;
    return REALISTIC_AVATARS.female[idx];
  }

  if (pref.includes('male')) {
    const idx = getHash(seed) % REALISTIC_AVATARS.male.length;
    return REALISTIC_AVATARS.male[idx];
  }

  if (pref.includes('non-binary') || pref.includes('neutral')) {
    const idx = getHash(seed) % REALISTIC_AVATARS.neutral.length;
    return REALISTIC_AVATARS.neutral[idx];
  }

  // Default: Return initials SVG URL (never random cartoon)
  return getInitialsSvgUrl(name, email);
}
