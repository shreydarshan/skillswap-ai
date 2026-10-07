import React, { useState } from 'react';
import { Sparkles, ArrowRight, MapPin, CheckCircle2, Repeat, Flame } from 'lucide-react';
import Card from '../common/Card';
import Button from '../common/Button';
import SkillTag from '../common/SkillTag';
import WhyMatchModal from '../swap/WhyMatchModal';
import SwapRequestModal from '../swap/SwapRequestModal';
import QuickProfileModal from './QuickProfileModal';
import ProfileAvatar from './ProfileAvatar';
import { authService } from '../../services/auth';
import { getAvatarUrl } from '../../utils/avatar';

export default function FeaturedMatchCard({ candidate, onSwapSuccess = null }) {
  const [showWhyModal, setShowWhyModal] = useState(false);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);

  if (!candidate) return null;

  const candidateName = candidate.candidate_name || candidate.name || candidate.full_name || 'Top Match';
  const roleText = candidate.role || (candidate.branch ? `${candidate.branch}${candidate.year ? ` • Year ${candidate.year}` : ''}` : 'Student');
  const universityText = candidate.university || candidate.college || '';
  const skillsOffered = candidate.skillsOffered || candidate.skills_offered || [];
  const skillsWanted = candidate.skillsWanted || candidate.skills_wanted || [];

  const rawMatchPct = typeof candidate.matchPercentage === 'number'
    ? candidate.matchPercentage
    : (candidate.hybrid_match_percentage !== undefined
      ? candidate.hybrid_match_percentage
      : (typeof candidate.hybrid_score === 'number'
        ? Math.round(candidate.hybrid_score * 100)
        : (typeof candidate.reciprocal_score === 'number' ? Math.round(candidate.reciprocal_score * 100) : 85)));

  const avatarUrl = getAvatarUrl(
    candidate.avatar || candidate.avatar_url,
    candidateName,
    candidate.email,
    candidate.gender_preference
  );

  const handleOpenProfile = () => {
    setShowProfileModal(true);
    const targetId = candidate.id || candidate.user_id || candidate.candidate_id;
    if (targetId) {
      authService.recordInteraction(targetId, 'VIEW').catch(() => {});
    }
  };

  const normalizedUser = {
    ...candidate,
    id: candidate.id || candidate.user_id || candidate.candidate_id,
    name: candidateName,
    full_name: candidateName,
    avatar: avatarUrl,
    avatar_url: avatarUrl,
    role: roleText,
    university: universityText,
    skillsOffered,
    skillsWanted,
    matchPercentage: rawMatchPct,
    matchLabel: 'Hybrid Match',
    matchReasons: candidate.match_reasons || [],
    forward_score: candidate.forward_score || candidate.match_scores?.forward_score || 0,
    reverse_score: candidate.reverse_score || candidate.match_scores?.reverse_score || 0,
    reciprocal_score: candidate.reciprocal_score || candidate.content_score || 0,
  };

  // Determine pronoun or name label
  const teachYouLabel = candidate.gender_preference === 'Female' ? 'She can teach you' : candidate.gender_preference === 'Male' ? 'He can teach you' : 'They can teach you';
  const teachThemLabel = candidate.gender_preference === 'Female' ? 'You can teach her' : candidate.gender_preference === 'Male' ? 'You can teach him' : 'You can teach them';

  return (
    <>
      <div className="relative overflow-hidden bg-gradient-to-br from-white via-blue-50/40 to-indigo-50/60 rounded-3xl border border-blue-200/80 shadow-lg shadow-blue-500/5 p-6 sm:p-7">
        {/* Ambient decorative background glow */}
        <div className="absolute top-0 right-0 w-80 h-80 bg-blue-400/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-10 left-10 w-60 h-60 bg-indigo-400/10 rounded-full blur-2xl pointer-events-none" />

        <div className="relative z-10">
          {/* Header Badge */}
          <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-blue-600 text-white rounded-full text-xs font-bold shadow-xs">
              <Flame className="w-3.5 h-3.5 text-amber-300" />
              <span>BEST MATCH FOR YOU</span>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-2xl font-black text-blue-600 tracking-tight">
                {rawMatchPct}%
              </span>
              <span className="text-[11px] font-bold uppercase tracking-wider text-blue-700 bg-blue-100/90 px-2.5 py-1 rounded-full border border-blue-200">
                Hybrid Compatibility
              </span>
            </div>
          </div>

          {/* Candidate Profile Info */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-5 border-b border-blue-100/80">
            <div className="flex items-center gap-4 min-w-0">
              <ProfileAvatar
                src={candidate.avatar || candidate.avatar_url}
                name={candidateName}
                email={candidate.email}
                genderPreference={candidate.gender_preference}
                size="xl"
                statusIndicator={true}
                onClick={handleOpenProfile}
                className="border-2 border-white shadow-md hover:scale-105 transition-transform"
              />

              <div className="min-w-0">
                <h3
                  onClick={handleOpenProfile}
                  className="text-xl sm:text-2xl font-extrabold text-slate-900 hover:text-blue-600 transition-colors cursor-pointer truncate"
                  title={candidateName}
                >
                  {candidateName}
                </h3>
                <p className="text-xs sm:text-sm font-semibold text-slate-600 truncate mt-0.5">
                  {roleText}
                </p>
                {universityText && (
                  <p className="flex items-center gap-1.5 text-xs text-slate-400 truncate mt-0.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span>{universityText}</span>
                  </p>
                )}
              </div>
            </div>

            {/* Reciprocal Indicator Pill */}
            <div className="flex items-center gap-2 px-3.5 py-1.5 bg-emerald-50 text-emerald-800 rounded-2xl border border-emerald-200/80 text-xs font-semibold self-start sm:self-auto">
              <Repeat className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
              <span>Strong 2-Way Skill Match</span>
            </div>
          </div>

          {/* Two-Way Exchange Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 py-5">
            {/* What they can teach you */}
            <div className="bg-white/90 backdrop-blur-xs rounded-2xl p-4 border border-blue-100/90 shadow-2xs">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-700 flex items-center gap-1.5 mb-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                {teachYouLabel}
              </span>
              <div className="flex flex-wrap gap-2">
                {skillsOffered.slice(0, 4).map((sk) => {
                  const sName = typeof sk === 'string' ? sk : sk.name;
                  const sId = typeof sk === 'object' && sk?.id ? sk.id : sName;
                  return <SkillTag key={sId} name={sName} variant="offer" size="md" />;
                })}
                {skillsOffered.length === 0 && (
                  <span className="text-xs text-slate-400 italic">No skills listed</span>
                )}
              </div>
            </div>

            {/* What you can teach them */}
            <div className="bg-white/90 backdrop-blur-xs rounded-2xl p-4 border border-blue-100/90 shadow-2xs">
              <span className="text-xs font-bold uppercase tracking-wider text-blue-700 flex items-center gap-1.5 mb-2">
                <span className="w-2 h-2 rounded-full bg-blue-500" />
                {teachThemLabel}
              </span>
              <div className="flex flex-wrap gap-2">
                {skillsWanted.slice(0, 4).map((sk) => {
                  const sName = typeof sk === 'string' ? sk : sk.name;
                  const sId = typeof sk === 'object' && sk?.id ? sk.id : sName;
                  return <SkillTag key={sId} name={sName} variant="want" size="md" />;
                })}
                {skillsWanted.length === 0 && (
                  <span className="text-xs text-slate-400 italic">No skills listed</span>
                )}
              </div>
            </div>
          </div>

          {/* Footer Actions */}
          <div className="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            <button
              onClick={() => setShowWhyModal(true)}
              className="inline-flex items-center gap-2 text-xs font-bold text-blue-600 hover:text-blue-700 bg-blue-50/80 hover:bg-blue-100 px-4 py-2.5 rounded-xl transition-colors cursor-pointer self-start sm:self-auto"
            >
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              <span>Why this match?</span>
              <ArrowRight className="w-3 h-3 text-blue-500" />
            </button>

            <div className="flex items-center gap-2.5">
              <Button
                variant="outline"
                size="md"
                onClick={handleOpenProfile}
                className="text-xs font-semibold px-4 py-2.5"
              >
                View Profile
              </Button>
              <Button
                variant="primary"
                size="md"
                onClick={() => setShowRequestModal(true)}
                className="text-xs font-bold px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-md shadow-blue-500/20"
              >
                Request Swap
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      <WhyMatchModal
        user={normalizedUser}
        isOpen={showWhyModal}
        onClose={() => setShowWhyModal(false)}
        onRequestSwap={() => {
          setShowWhyModal(false);
          setShowRequestModal(true);
        }}
      />

      <SwapRequestModal
        user={normalizedUser}
        isOpen={showRequestModal}
        onClose={() => setShowRequestModal(false)}
        onSuccess={onSwapSuccess}
      />

      <QuickProfileModal
        user={normalizedUser}
        isOpen={showProfileModal}
        onClose={() => setShowProfileModal(false)}
        onRequestSwap={() => {
          setShowProfileModal(false);
          setShowRequestModal(true);
        }}
      />
    </>
  );
}
