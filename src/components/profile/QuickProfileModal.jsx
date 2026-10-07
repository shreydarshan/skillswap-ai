import React from 'react';
import { useNavigate } from 'react-router-dom';
import { X, Star, MapPin, Award, CheckCircle2, Clock, Calendar, MessageSquare, Check, Sparkles } from 'lucide-react';
import Button from '../common/Button';
import SkillTag from '../common/SkillTag';
import MatchBadge from '../common/MatchBadge';
import ProfileAvatar from './ProfileAvatar';
import { getAvatarUrl } from '../../utils/avatar';
import { useAuth } from '../../context/AuthContext';

export default function QuickProfileModal({ user, isOpen, onClose, onRequestSwap, onChat }) {
  const navigate = useNavigate();
  const { getRelationshipWithUser, user: currentUser } = useAuth();

  if (!isOpen || !user) return null;

  const targetId = user.id || user.user_id || user.candidate_id;
  const relationship = getRelationshipWithUser ? getRelationshipWithUser(targetId) : { status: 'NO_RELATIONSHIP' };
  const isSelf = currentUser?.id && String(currentUser.id) === String(targetId);

  const handleSendMessage = () => {
    onClose();
    if (onChat) {
      onChat(user);
    } else {
      navigate('/app/chats', {
        state: {
          recipientId: targetId,
          recipientUser: user
        }
      });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-white w-full max-w-2xl rounded-3xl border border-slate-200 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Scrollable Content Container */}
        <div className="overflow-y-auto flex-1 overscroll-contain">
          {/* 1. Decorative Header Banner */}
          <div className="relative h-24 sm:h-28 bg-gradient-to-r from-blue-600/15 via-indigo-600/10 to-violet-600/15 border-b border-slate-100 shrink-0">
            <div className="absolute inset-0 bg-[radial-gradient(#3b82f6_1px,transparent_1px)] [background-size:16px_16px] opacity-15 pointer-events-none" />
            <button
              onClick={onClose}
              className="absolute top-3.5 right-3.5 p-2 rounded-full bg-white/90 hover:bg-white text-slate-700 shadow-sm transition-colors z-20 cursor-pointer"
              title="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* 2. Profile Identity & Details */}
          <div className="px-6 pb-6 pt-0 space-y-6">
            {/* Identity Row: Avatar + Name/Details + Match Badge */}
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
              <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                {/* Avatar overlapping banner safely with controlled negative margin ONLY on avatar */}
                <div className="-mt-12 sm:-mt-14 relative z-10 shrink-0">
                  <ProfileAvatar
                    src={user.avatar || user.avatar_url}
                    name={user.name}
                    email={user.email}
                    genderPreference={user.gender_preference}
                    size="xl"
                    className="border-4 border-white shadow-md bg-white rounded-3xl shrink-0"
                  />
                </div>

                {/* Identity Information strictly in normal flow */}
                <div className="space-y-1 min-w-0 pt-1 sm:pt-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="text-xl font-extrabold text-slate-900 tracking-tight">{user.name}</h3>
                    {relationship.isConnected && (
                      <span className="px-2.5 py-0.5 bg-emerald-50 text-emerald-700 text-xs font-bold rounded-full border border-emerald-200 flex items-center gap-1">
                        <Check className="w-3 h-3 stroke-[2.5]" /> Connected
                      </span>
                    )}
                    {relationship.isPending && (
                      <span className="px-2.5 py-0.5 bg-amber-50 text-amber-700 text-xs font-bold rounded-full border border-amber-200 flex items-center gap-1">
                        <Clock className="w-3 h-3" /> Pending Swap
                      </span>
                    )}
                    {user.badge && !relationship.isConnected && !relationship.isPending && (
                      <span className="px-2.5 py-0.5 bg-blue-50 text-blue-700 text-xs font-semibold rounded-full border border-blue-200">
                        {user.badge}
                      </span>
                    )}
                  </div>

                  <p className="text-sm font-medium text-slate-600">{user.role}</p>

                  <div className="flex items-center gap-3 text-xs text-slate-500 pt-0.5 flex-wrap">
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      {user.university || 'Campus'}
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1 font-semibold text-amber-600">
                      <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400 shrink-0" />
                      {user.rating || 5.0} ({user.reviewCount || 12} reviews)
                    </span>
                  </div>
                </div>
              </div>

              {/* Match Badge anchored cleanly without overlapping */}
              {user.matchPercentage && (
                <div className="shrink-0 self-start sm:self-center pt-1 sm:pt-2">
                  <MatchBadge percentage={user.matchPercentage} size="lg" />
                </div>
              )}
            </div>

            {/* 3. About Section */}
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">About Me</h4>
              <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-200/60">
                {user.bio || "Student ready to exchange skills and learn together."}
              </p>
            </div>

            {/* 4. Skills Section */}
            <div className="grid sm:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl border border-blue-100 bg-blue-50/40 space-y-2">
                <h4 className="text-xs font-bold text-blue-700 uppercase tracking-wider flex items-center gap-1.5">
                  <Award className="w-3.5 h-3.5" /> Skills Offered
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {user.skillsOffered?.map((s, idx) => (
                    <SkillTag key={idx} name={typeof s === 'string' ? s : s.name} variant="offer" badge={s.level} />
                  ))}
                  {(!user.skillsOffered || user.skillsOffered.length === 0) && (
                    <span className="text-xs text-slate-400">None listed</span>
                  )}
                </div>
              </div>

              <div className="p-4 rounded-xl border border-emerald-100 bg-emerald-50/40 space-y-2">
                <h4 className="text-xs font-bold text-emerald-700 uppercase tracking-wider flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Wants to Learn
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {user.skillsWanted?.map((s, idx) => (
                    <SkillTag key={idx} name={typeof s === 'string' ? s : s.name} variant="want" badge={s.urgency} />
                  ))}
                  {(!user.skillsWanted || user.skillsWanted.length === 0) && (
                    <span className="text-xs text-slate-400">None listed</span>
                  )}
                </div>
              </div>
            </div>

            {/* 5. Availability & Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60 text-xs">
                <span className="text-slate-400 block mb-0.5">Availability</span>
                <span className="font-semibold text-slate-800">{user.availability || 'Flexible'}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60 text-xs">
                <span className="text-slate-400 block mb-0.5">Completed Swaps</span>
                <span className="font-semibold text-slate-800">{user.completedSwaps || 0} Sessions</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60 text-xs col-span-2 sm:col-span-1">
                <span className="text-slate-400 block mb-0.5">Response Time</span>
                <span className="font-semibold text-slate-800">{user.responseTime || '< 1 hr'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* 6. Docked Footer Actions — Respects Relationship State */}
        <div className="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between gap-3 shrink-0">
          {isSelf ? (
            <div className="w-full flex justify-end">
              <Button variant="outline" size="md" onClick={onClose}>Close</Button>
            </div>
          ) : relationship.isConnected ? (
            <>
              <Button
                variant="outline"
                size="md"
                onClick={onClose}
              >
                Close
              </Button>
              <Button
                variant="primary"
                size="md"
                icon={MessageSquare}
                onClick={handleSendMessage}
                className="bg-emerald-600 hover:bg-emerald-700"
              >
                Open Chat
              </Button>
            </>
          ) : relationship.isPending ? (
            <>
              <Button
                variant="outline"
                size="md"
                icon={MessageSquare}
                onClick={handleSendMessage}
              >
                Send Message
              </Button>
              <Button
                variant="secondary"
                size="md"
                disabled
                className="bg-amber-50 text-amber-700 border border-amber-200 cursor-not-allowed opacity-90 font-medium"
              >
                Pending Request
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="outline"
                size="md"
                icon={MessageSquare}
                onClick={handleSendMessage}
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
            </>
          )}
        </div>
      </div>
    </div>
  );
}
