import React from 'react';
import { X, Star, MapPin, Award, CheckCircle2, Clock, Calendar, MessageSquare } from 'lucide-react';
import Button from '../common/Button';
import SkillTag from '../common/SkillTag';
import MatchBadge from '../common/MatchBadge';
import ProfileAvatar from './ProfileAvatar';
import { getAvatarUrl } from '../../utils/avatar';

export default function QuickProfileModal({ user, isOpen, onClose, onRequestSwap, onChat }) {
  if (!isOpen || !user) return null;

  const avatarSrc = getAvatarUrl(user.avatar || user.avatar_url, user.name, user.email, user.gender_preference);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-white w-full max-w-2xl rounded-2xl border border-slate-200 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Banner */}
        <div className="h-20 bg-gradient-to-r from-slate-50 via-blue-50/40 to-indigo-50/50 border-b border-slate-100 relative">
          <div className="absolute inset-0 bg-[radial-gradient(#3b82f6_1px,transparent_1px)] [background-size:16px_16px] opacity-10 pointer-events-none" />
          <button
            onClick={onClose}
            className="absolute top-3.5 right-3.5 p-1.5 rounded-full bg-slate-200/70 hover:bg-slate-300 text-slate-700 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Profile Content */}
        <div className="px-6 pb-6 pt-0 space-y-6 overflow-y-auto flex-1">
          {/* Top Info */}
          <div className="flex flex-col sm:flex-row sm:items-end justify-between -mt-10 gap-4">
            <div className="flex flex-col sm:flex-row sm:items-end gap-4">
              <ProfileAvatar
                src={user.avatar || user.avatar_url}
                name={user.name}
                email={user.email}
                genderPreference={user.gender_preference}
                size="xl"
                className="border-4 border-white shadow-md bg-white rounded-3xl shrink-0"
              />
              <div className="space-y-0.5 pb-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-xl font-extrabold text-slate-900 tracking-tight">{user.name}</h3>
                  {user.badge && (
                    <span className="px-2.5 py-0.5 bg-blue-50 text-blue-700 text-xs font-semibold rounded-full border border-blue-200">
                      {user.badge}
                    </span>
                  )}
                </div>
                <p className="text-sm font-medium text-slate-600">{user.role}</p>
                <div className="flex items-center gap-3 text-xs text-slate-500 pt-0.5">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    {user.university}
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1 font-semibold text-amber-600">
                    <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                    {user.rating} ({user.reviewCount || 12} reviews)
                  </span>
                </div>
              </div>
            </div>

            {user.matchPercentage && (
              <div className="self-start sm:self-end pb-1">
                <MatchBadge percentage={user.matchPercentage} size="lg" />
              </div>
            )}
          </div>

          {/* Bio */}
          <div>
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">About Me</h4>
            <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-200/60">
              {user.bio}
            </p>
          </div>

          {/* Skills Offered & Wanted */}
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl border border-blue-100 bg-blue-50/40 space-y-2">
              <h4 className="text-xs font-bold text-blue-700 uppercase tracking-wider flex items-center gap-1.5">
                <Award className="w-3.5 h-3.5" /> Skills Offered
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {user.skillsOffered?.map((s, idx) => (
                  <SkillTag key={idx} name={s.name} variant="offer" badge={s.level} />
                ))}
              </div>
            </div>

            <div className="p-4 rounded-xl border border-emerald-100 bg-emerald-50/40 space-y-2">
              <h4 className="text-xs font-bold text-emerald-700 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" /> Wants to Learn
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {user.skillsWanted?.map((s, idx) => (
                  <SkillTag key={idx} name={s.name} variant="want" badge={s.urgency} />
                ))}
              </div>
            </div>
          </div>

          {/* Availability & Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60 text-xs">
              <span className="text-slate-400 block mb-0.5">Availability</span>
              <span className="font-semibold text-slate-800">{user.availability}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60 text-xs">
              <span className="text-slate-400 block mb-0.5">Completed Swaps</span>
              <span className="font-semibold text-slate-800">{user.completedSwaps} Sessions</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60 text-xs col-span-2 sm:col-span-1">
              <span className="text-slate-400 block mb-0.5">Response Time</span>
              <span className="font-semibold text-slate-800">{user.responseTime || '< 1 hr'}</span>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between gap-3">
          <Button
            variant="outline"
            size="md"
            icon={MessageSquare}
            onClick={() => {
              onClose();
              if (onChat) onChat(user);
            }}
          >
            Send Message
          </Button>
          <Button
            variant="primary"
            size="md"
            onClick={() => {
              onClose();
              if (onRequestSwap) onRequestSwap(user);
            }}
          >
            Request Swap
          </Button>
        </div>
      </div>
    </div>
  );
}
