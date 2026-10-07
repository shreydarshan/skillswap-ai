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

export default function ProfileCard({ user, onSwapSuccess = null, onOpenChat = null }) {
  const [showWhyModal, setShowWhyModal] = useState(false);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);

  const handleOpenProfile = () => {
    setShowProfileModal(true);
    const targetId = user.id || user.user_id || user.candidate_id;
    if (targetId) {
      authService.recordInteraction(targetId, 'VIEW').catch(() => {});
    }
  };

  const candidateName = user.name || user.full_name || 'Student';
  const roleText = user.role || (user.branch ? `${user.branch}${user.year ? ` • Year ${user.year}` : ''}` : 'Student');
  const universityText = user.university || user.college || '';
  const skillsOffered = user.skillsOffered || user.skills_offered || [];
  const skillsWanted = user.skillsWanted || user.skills_wanted || [];

  const rawMatchPct = typeof user.matchPercentage === 'number'
    ? user.matchPercentage
    : (user.hybrid_match_percentage !== undefined
      ? user.hybrid_match_percentage
      : (typeof user.reciprocal_score === 'number' ? Math.round(user.reciprocal_score * 100) : null));

  const matchLabel = user.matchLabel || (
    user.hybrid_score !== undefined || user.hybrid_match_percentage !== undefined
      ? 'Hybrid Match'
      : 'Match'
  );

  const avatarUrl = getAvatarUrl(
    user.avatar || user.avatar_url,
    candidateName,
    user.email,
    user.gender_preference
  );

  const normalizedUser = {
    ...user,
    name: candidateName,
    full_name: candidateName,
    avatar: avatarUrl,
    avatar_url: avatarUrl,
    role: roleText,
    university: universityText,
    skillsOffered,
    skillsWanted,
    matchPercentage: rawMatchPct,
    matchLabel,
  };

  // Only display bio if genuine and not repetitive placeholder
  const hasCustomBio = user.bio && !user.bio.toLowerCase().includes('ready to exchange skills');

  return (
    <>
      <Card hoverEffect className="flex flex-col justify-between h-full group p-5 border-slate-200/90 shadow-2xs hover:shadow-md transition-all">
        <div>
          {/* Card Top: Avatar, Student Info, Match Badge */}
          <div className="flex items-start justify-between gap-3 mb-3.5">
            <div className="flex items-center gap-3 min-w-0">
              <ProfileAvatar
                src={user.avatar || user.avatar_url}
                name={candidateName}
                email={user.email}
                genderPreference={user.gender_preference}
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
                <MatchBadge percentage={rawMatchPct} label={matchLabel} size="sm" />
              </div>
            )}
          </div>

          {/* Genuine custom bio only (if present and not repetitive filler) */}
          {hasCustomBio && (
            <p className="text-xs text-slate-600 line-clamp-2 mb-3 leading-relaxed">
              {user.bio}
            </p>
          )}

          {/* Teaches / Offers (OFFERS) */}
          <div className="mb-2.5">
            <span className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
              Teaches:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {skillsOffered.slice(0, 3).map((sk) => {
                const sName = typeof sk === 'string' ? sk : sk.name;
                const sId = typeof sk === 'object' && sk?.id ? sk.id : sName;
                return <SkillTag key={sId} name={sName} variant="offer" size="sm" />;
              })}
              {skillsOffered.length > 3 && (
                <span className="text-[11px] text-slate-400 self-center pl-0.5 font-medium">
                  +{skillsOffered.length - 3}
                </span>
              )}
              {skillsOffered.length === 0 && (
                <span className="text-[11px] text-slate-400 italic">No skills listed</span>
              )}
            </div>
          </div>

          {/* Wants to Learn (WANTS) */}
          <div className="mb-3.5">
            <span className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
              Wants to Learn:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {skillsWanted.slice(0, 3).map((sk) => {
                const sName = typeof sk === 'string' ? sk : sk.name;
                const sId = typeof sk === 'object' && sk?.id ? sk.id : sName;
                return <SkillTag key={sId} name={sName} variant="want" size="sm" />;
              })}
              {skillsWanted.length > 3 && (
                <span className="text-[11px] text-slate-400 self-center pl-0.5 font-medium">
                  +{skillsWanted.length - 3}
                </span>
              )}
              {skillsWanted.length === 0 && (
                <span className="text-[11px] text-slate-400 italic">No skills listed</span>
              )}
            </div>
          </div>
        </div>

        {/* Card Footer Actions */}
        <div className="pt-3 border-t border-slate-100 flex flex-col gap-2">
          {/* Why this match link */}
          {typeof rawMatchPct === 'number' && rawMatchPct > 0 && (
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
          )}

          <div className="grid grid-cols-2 gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleOpenProfile}
              className="w-full text-xs"
            >
              View Profile
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => setShowRequestModal(true)}
              className="w-full text-xs"
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
