import React from 'react';
import { X, CheckCircle2, ArrowRightLeft, BookOpen, GraduationCap, Check } from 'lucide-react';
import Button from '../common/Button';
import SkillTag from '../common/SkillTag';
import ProfileAvatar from '../profile/ProfileAvatar';

export default function WhyMatchModal({ user, isOpen, onClose, onRequestSwap }) {
  if (!isOpen || !user) return null;

  const matchPercentage = typeof user.matchPercentage === 'number'
    ? user.matchPercentage
    : (user.reciprocal_score ? Math.round(user.reciprocal_score * 100) : 0);

  const forwardPct = typeof user.forward_score === 'number'
    ? Math.round(user.forward_score * 100)
    : (user.match_scores?.forward_score ? Math.round(user.match_scores.forward_score * 100) : null);

  const reversePct = typeof user.reverse_score === 'number'
    ? Math.round(user.reverse_score * 100)
    : (user.match_scores?.reverse_score ? Math.round(user.match_scores.reverse_score * 100) : null);

  const matchingWanted = user.matching_wanted_skills || [];
  const matchingOffered = user.matching_offered_skills || [];
  const reasons = user.matchReasons || user.match_reasons || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-white w-full max-w-lg rounded-2xl border border-slate-200 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ArrowRightLeft className="w-5 h-5 text-blue-200" />
            <h3 className="font-bold text-lg">
              {user.hybrid_score !== undefined || user.hybrid_match_percentage !== undefined
                ? 'Hybrid Recommendation Breakdown'
                : 'Reciprocal Skill Match Breakdown'}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-white/80 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 overflow-y-auto flex-1">
          {/* Student Header */}
          <div className="flex items-center gap-4 p-3 bg-slate-50 rounded-xl border border-slate-200/70">
            <ProfileAvatar
              src={user.avatar || user.avatar_url}
              name={user.name || user.full_name}
              email={user.email}
              genderPreference={user.gender_preference}
              size="md"
              className="rounded-full border border-white shadow-xs"
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h4 className="font-bold text-slate-900 truncate">{user.name || user.full_name}</h4>
                <span className="px-2 py-0.5 bg-blue-100 text-blue-700 font-semibold text-xs rounded-full shrink-0">
                  {matchPercentage}% {user.hybrid_score !== undefined ? 'Hybrid Match' : 'Reciprocal Match'}
                </span>
              </div>
              <p className="text-xs text-slate-500 truncate">
                {user.role || (user.branch ? `${user.branch} (${user.college || 'Campus'})` : 'Student')}
              </p>
            </div>
          </div>

          {/* Key Match Drivers */}
          <div>
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
              Why this match?
            </h4>
            <div className="space-y-2.5">
              {reasons.length > 0 ? (
                reasons.map((reason, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 p-3 bg-blue-50/50 border border-blue-100 rounded-xl text-xs text-slate-700"
                  >
                    <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                    <span className="leading-relaxed font-medium">{reason}</span>
                  </div>
                ))
              ) : (
                <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-600">
                  Calculated using content-based cosine similarity between your offered/wanted skills and {user.name || user.full_name}'s skills.
                </div>
              )}
            </div>
          </div>

          {/* Overlapping Skill Tags (if available) */}
          {(matchingWanted.length > 0 || matchingOffered.length > 0) && (
            <div className="space-y-3 p-3.5 bg-slate-50/70 border border-slate-200/60 rounded-xl">
              {matchingWanted.length > 0 && (
                <div>
                  <span className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                    <GraduationCap className="w-3.5 h-3.5 text-blue-600" /> They Teach You:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {matchingWanted.map((s, i) => (
                      <SkillTag key={i} name={s} variant="offer" size="sm" />
                    ))}
                  </div>
                </div>
              )}

              {matchingOffered.length > 0 && (
                <div>
                  <span className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                    <BookOpen className="w-3.5 h-3.5 text-indigo-600" /> You Teach Them:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {matchingOffered.map((s, i) => (
                      <SkillTag key={i} name={s} variant="want" size="sm" />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Recommendation Signal / Hybrid Explanation */}
          {user.is_collaborative_available ? (
            <div className="p-3.5 bg-indigo-50/70 border border-indigo-100 rounded-xl space-y-2">
              <span className="block text-[11px] font-bold text-indigo-700 uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-indigo-600" /> Why this recommendation?
              </span>
              <div className="space-y-1.5 text-xs text-slate-700">
                <div className="flex items-center gap-2">
                  <Check className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span className="font-medium">Strong reciprocal skill match</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
                  <span className="font-medium">Similar students also engaged with this student</span>
                </div>
              </div>
            </div>
          ) : user.hybrid_score !== undefined || user.hybrid_match_percentage !== undefined ? (
            <div className="p-3 bg-slate-50 border border-slate-200/80 rounded-xl flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-600">Recommendation Signal:</span>
              <span className="text-xs font-bold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200">
                Based on your skills
              </span>
            </div>
          ) : null}

          {/* Directional Cosine Scores */}
          {(forwardPct !== null || reversePct !== null) && (
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60">
                <span className="text-[11px] font-semibold text-slate-400 block mb-0.5">
                  Your Learning Need
                </span>
                <span className="font-bold text-sm text-slate-900">
                  {forwardPct !== null ? `${forwardPct}%` : '—'}
                </span>
                <p className="text-[10px] text-slate-500 mt-0.5">
                  Candidate offers what you want
                </p>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60">
                <span className="text-[11px] font-semibold text-slate-400 block mb-0.5">
                  Their Learning Need
                </span>
                <span className="font-bold text-sm text-slate-900">
                  {reversePct !== null ? `${reversePct}%` : '—'}
                </span>
                <p className="text-[10px] text-slate-500 mt-0.5">
                  You offer what candidate wants
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-end gap-3">
          <Button variant="outline" size="md" onClick={onClose}>
            Close
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
