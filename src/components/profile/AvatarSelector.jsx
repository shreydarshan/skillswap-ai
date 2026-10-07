import React from 'react';
import { Check } from 'lucide-react';
import ProfileAvatar from './ProfileAvatar';
import { REALISTIC_AVATARS, getRealisticPhotoUrl } from '../../utils/avatar';

export default function AvatarSelector({
  value = '',
  onChange,
  name = '',
  email = '',
}) {
  const options = [
    {
      id: '',
      label: 'Initials Avatar',
      sublabel: 'Default letter badge',
      preference: '',
    },
    {
      id: 'Female',
      label: 'Female Portrait',
      sublabel: 'Realistic student portrait',
      preference: 'Female',
    },
    {
      id: 'Male',
      label: 'Male Portrait',
      sublabel: 'Realistic student portrait',
      preference: 'Male',
    },
    {
      id: 'Non-binary / Neutral',
      label: 'Neutral Portrait',
      sublabel: 'Realistic student portrait',
      preference: 'Non-binary / Neutral',
    },
  ];

  const handleSelect = (opt) => {
    const photoUrl = opt.preference ? getRealisticPhotoUrl(opt.preference, name || email) : null;
    onChange(opt.id, photoUrl);
  };

  return (
    <div className="space-y-3">
      <div>
        <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
          Profile Photo Style (Optional)
        </label>
        <p className="text-xs text-slate-500">
          Choose a realistic student photo style or display your neutral initials badge.
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {options.map((opt) => {
          const isSelected = (value || '') === opt.id;
          return (
            <button
              key={opt.label}
              type="button"
              onClick={() => handleSelect(opt)}
              className={`p-3 rounded-2xl border text-left flex flex-col items-center text-center transition-all cursor-pointer relative group ${
                isSelected
                  ? 'border-blue-600 bg-blue-50/80 ring-2 ring-blue-600/20 shadow-xs'
                  : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/70'
              }`}
            >
              {isSelected && (
                <div className="absolute top-2 right-2 w-4 h-4 bg-blue-600 rounded-full flex items-center justify-center text-white">
                  <Check className="w-2.5 h-2.5 stroke-[3]" />
                </div>
              )}

              <ProfileAvatar
                name={name}
                email={email}
                genderPreference={opt.preference}
                size="md"
                className="mb-2"
              />

              <span className="text-xs font-bold text-slate-900 block leading-tight">
                {opt.label}
              </span>
              <span className="text-[10px] text-slate-500 block mt-0.5">
                {opt.sublabel}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
