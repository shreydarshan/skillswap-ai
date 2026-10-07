import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, BookOpen, Sparkles, Edit3 } from 'lucide-react';
import SkillTag from '../common/SkillTag';
import Button from '../common/Button';

export default function PersonalSkillSnapshot({ mySkills = [] }) {
  const navigate = useNavigate();

  const offeredSkills = mySkills.filter((s) => s.skill_type === 'OFFER');
  const wantedSkills = mySkills.filter((s) => s.skill_type === 'WANT');

  return (
    <div className="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200/90 shadow-2xs hover:shadow-xs transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-100">
            Your Exchange Profile
          </span>
        </div>

        <button
          onClick={() => navigate('/app/profile')}
          className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-600 hover:text-blue-700 cursor-pointer"
        >
          <Edit3 className="w-3.5 h-3.5" />
          <span>Edit Skills</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* You Teach */}
        <div className="bg-emerald-50/50 rounded-2xl p-3.5 border border-emerald-100/80">
          <div className="flex items-center gap-1.5 mb-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="text-xs font-bold text-emerald-800 uppercase tracking-wide">
              You Teach
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5 min-h-[30px] items-center">
            {offeredSkills.length > 0 ? (
              offeredSkills.map((s) => (
                <SkillTag key={s.id || s.skill_id} name={s.skill_name || s.skill?.name || s.name} variant="offer" size="sm" />
              ))
            ) : (
              <span className="text-xs text-slate-400 italic">No teaching skills added yet</span>
            )}
          </div>
        </div>

        {/* You Want to Learn */}
        <div className="bg-blue-50/50 rounded-2xl p-3.5 border border-blue-100/80">
          <div className="flex items-center gap-1.5 mb-2">
            <span className="w-2 h-2 rounded-full bg-blue-500" />
            <span className="text-xs font-bold text-blue-800 uppercase tracking-wide">
              You Want to Learn
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5 min-h-[30px] items-center">
            {wantedSkills.length > 0 ? (
              wantedSkills.map((s) => (
                <SkillTag key={s.id || s.skill_id} name={s.skill_name || s.skill?.name || s.name} variant="want" size="sm" />
              ))
            ) : (
              <span className="text-xs text-slate-400 italic">No learning goals added yet</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
