import React, { useState } from 'react';
import { MapPin, GraduationCap } from 'lucide-react';
import Card from '../common/Card';
import Button from '../common/Button';
import SkillTag from '../common/SkillTag';
import SwapRequestModal from '../swap/SwapRequestModal';
import QuickProfileModal from './QuickProfileModal';
import ProfileAvatar from './ProfileAvatar';
import { authService } from '../../services/auth';
import { getAvatarUrl } from '../../utils/avatar';

export default function ExploreStudentCard({ student, onSwapSuccess = null }) {
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);

  const studentName = student.name || student.full_name || 'Student';
  const roleText = student.role || (student.branch ? `${student.branch}${student.year ? ` • Year ${student.year}` : ''}` : 'Student');
  const universityText = student.university || student.college || '';
  const skillsOffered = student.skillsOffered || student.skills_offered || [];
  const skillsWanted = student.skillsWanted || student.skills_wanted || [];

  const avatarUrl = getAvatarUrl(
    student.avatar || student.avatar_url,
    studentName,
    student.email,
    student.gender_preference
  );

  const handleOpenProfile = () => {
    setShowProfileModal(true);
    const targetId = student.id || student.user_id;
    if (targetId) {
      authService.recordInteraction(targetId, 'VIEW').catch(() => {});
    }
  };

  const normalizedStudent = {
    ...student,
    name: studentName,
    full_name: studentName,
    avatar: avatarUrl,
    avatar_url: avatarUrl,
    role: roleText,
    university: universityText,
    skillsOffered,
    skillsWanted,
  };

  // Only show custom bio if genuine and not repetitive placeholder
  const customBio = student.bio && !student.bio.toLowerCase().includes('ready to exchange skills')
    ? student.bio
    : null;

  return (
    <>
      <Card hoverEffect className="flex flex-col justify-between h-full group p-5 border-slate-200/90 shadow-2xs hover:shadow-md hover:border-blue-200 transition-all bg-white rounded-2xl">
        <div>
          {/* Header: Avatar, Name, College */}
          <div className="flex items-start gap-3.5 mb-3.5">
            <ProfileAvatar
              src={student.avatar || student.avatar_url}
              name={studentName}
              email={student.email}
              genderPreference={student.gender_preference}
              size="lg"
              statusIndicator={true}
              onClick={handleOpenProfile}
              className="group-hover:scale-105 transition-transform duration-200"
            />

            <div className="min-w-0 flex-1">
              <h3
                onClick={handleOpenProfile}
                className="font-bold text-slate-900 text-base group-hover:text-blue-600 transition-colors cursor-pointer truncate leading-snug"
                title={studentName}
              >
                {studentName}
              </h3>
              <p className="text-xs text-slate-500 font-medium truncate mt-0.5 flex items-center gap-1">
                <GraduationCap className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span>{roleText}</span>
              </p>
              {universityText && (
                <p className="flex items-center gap-1 text-[11px] text-slate-400 truncate mt-0.5">
                  <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
                  <span>{universityText}</span>
                </p>
              )}
            </div>
          </div>

          {/* Short Bio (if genuine) */}
          {customBio && (
            <p className="text-xs text-slate-600 line-clamp-2 mb-3.5 leading-relaxed">
              {customBio}
            </p>
          )}

          {/* TEACHES */}
          <div className="mb-3">
            <span className="block text-[10px] font-bold uppercase tracking-wider text-emerald-700/80 mb-1.5 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" />
              Teaches
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

          {/* WANTS */}
          <div className="mb-4">
            <span className="block text-[10px] font-bold uppercase tracking-wider text-blue-700/80 mb-1.5 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500 inline-block" />
              Wants to Learn
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

        {/* Footer Actions — View Profile & Request Swap */}
        <div className="pt-3 border-t border-slate-100 grid grid-cols-2 gap-2 mt-auto">
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
      </Card>

      {/* Modals */}
      <SwapRequestModal
        user={normalizedStudent}
        isOpen={showRequestModal}
        onClose={() => setShowRequestModal(false)}
        onSuccess={onSwapSuccess}
      />

      <QuickProfileModal
        user={normalizedStudent}
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
