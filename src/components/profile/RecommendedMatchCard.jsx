import React, { useState } from 'react';
import { MapPin, Sparkles, ArrowRight } from 'lucide-react';
import Card from '../common/Card';
import Button from '../common/Button';
import SkillTag from '../common/SkillTag';
import MatchBadge from '../common/MatchBadge';
import WhyMatchModal from '../swap/WhyMatchModal';
import SwapRequestModal from '../swap/SwapRequestModal';
import QuickProfileModal from './QuickProfileModal';
import ProfileAvatar from './ProfileAvatar';
import { authService } from '../../services/auth';
import { getAvatarUrl } from '../../utils/avatar';

export default function RecommendedMatchCard({ candidate, onSwapSuccess = null }) {
  const [showWhyModal, setShowWhyModal] = useState(false);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);

  if (!candidate) return null;

  const candidateName = candidate.candidate_name || candidate.name || candidate.full_name || 'Match';
  const roleText = candidate.role || (candidate.branch ? `${candidate.branch}${candidate.year ? ` • Yr ${candidate.year}` : ''}` : 'Student');
  const universityText = candidate.university || candidate.college || '';
  const skillsOffered = candidate.skillsOffered || candidate.skills_offered || [];
  const skillsWanted = candidate.skillsWanted || candidate.skills_wanted || [];

  const rawMatchPct = typeof candidate.matchPercentage === 'number'
    ? candidate.matchPercentage
    : (candidate.hybrid_match_percentage !== undefined
      ? candidate.hybrid_match_percentage
      : (typeof candidate.hybrid_score === 'number'
        ? Math.round(candidate.hybrid_score * 100)
        : (typeof candidate.reciprocal_score === 'number' ? Math.round(candidate.reciprocal_score * 100) : null)));

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

  return (
    <>
      <Card hoverEffect className="flex flex-col justify-between h-full group p-5 border-slate-200/90 shadow-2xs hover:shadow-md hover:border-blue-200 transition-all bg-white rounded-2xl">
        <div>
          {/* Top Row: Avatar, Student Info, Match Badge */}
          <div className="flex items-start justify-between gap-3 mb-3.5">
            <div className="flex items-center gap-3 min-w-0">
              <ProfileAvatar
                src={candidate.avatar || candidate.avatar_url}
                name={candidateName}
                email={candidate.email}
                genderPreference={candidate.gender_preference}
                size="md"
                statusIndicator={true}
                onClick={handleOpenProfile}
                className="group-hover:scale-105 transition-transform duration-200"
              />
              <div className="min-w-0">
                <h3
                  onClick={handleOpenProfile}
                  className="font-bold text-slate-900 text-sm sm:text-base group-hover:text-blue-600 transition-colors cursor-pointer truncate leading-snug"
                  title={candidateName}
                >
                  {candidateName}
                </h3>
                <p className="text-xs text-slate-500 font-medium truncate mt-0.5">
                  {roleText}
                </p>
                {universityText && (
                  <p className="flex items-center gap-1 text-[11px] text-slate-400 truncate mt-0.5">
                    <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
                    <span>{universityText}</span>
                  </p>
                )}
              </div>
            </div>

            {typeof rawMatchPct === 'number' && rawMatchPct > 0 && (
              <div className="shrink-0">
                <MatchBadge percentage={rawMatchPct} label="Match" size="sm" />
              </div>
            )}
          </div>

          {/* Teaches */}
          <div className="mb-2.5">
            <span className="block text-[10px] font-bold uppercase tracking-wider text-emerald-700/80 mb-1.5 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              Teaches
            </span>
            <div className="flex flex-wrap gap-1.5">
              {skillsOffered.slice(0, 2).map((sk) => {
                const sName = typeof sk === 'string' ? sk : sk.name;
                const sId = typeof sk === 'object' && sk?.id ? sk.id : sName;
                return <SkillTag key={sId} name={sName} variant="offer" size="sm" />;
              })}
              {skillsOffered.length > 2 && (
                <span className="text-[11px] text-slate-400 self-center pl-0.5 font-medium">
                  +{skillsOffered.length - 2}
                </span>
              )}
            </div>
          </div>

          {/* Wants */}
          <div className="mb-3.5">
            <span className="block text-[10px] font-bold uppercase tracking-wider text-blue-700/80 mb-1.5 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
              Wants
            </span>
            <div className="flex flex-wrap gap-1.5">
              {skillsWanted.slice(0, 2).map((sk) => {
                const sName = typeof sk === 'string' ? sk : sk.name;
                const sId = typeof sk === 'object' && sk?.id ? sk.id : sName;
                return <SkillTag key={sId} name={sName} variant="want" size="sm" />;
              })}
              {skillsWanted.length > 2 && (
                <span className="text-[11px] text-slate-400 self-center pl-0.5 font-medium">
                  +{skillsWanted.length - 2}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Card Footer Actions */}
        <div className="pt-3 border-t border-slate-100 flex flex-col gap-2 mt-auto">
          {/* Why this match button */}
          <button
            onClick={() => setShowWhyModal(true)}
            className="flex items-center justify-between text-xs font-semibold text-blue-600 hover:text-blue-700 bg-blue-50/70 hover:bg-blue-100/70 px-3 py-1.5 rounded-xl transition-colors cursor-pointer"
          >
            <span className="flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              Why this match?
            </span>
            <ArrowRight className="w-3 h-3 text-blue-500" />
          </button>

          <div className="grid grid-cols-2 gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleOpenProfile}
              className="w-full text-xs font-semibold py-2"
            >
              View Profile
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => setShowRequestModal(true)}
              className="w-full text-xs font-semibold py-2"
            >
              Request Swap
            </Button>
          </div>
        </div>
      </Card>

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
