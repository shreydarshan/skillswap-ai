import React from 'react';
import { ArrowUpDown, Plus, Sparkles } from 'lucide-react';

export default function ReciprocalExplainer({ mySkills = [], featuredCandidate = null }) {
  // Extract user's actual database skills
  const offered = mySkills.filter((s) => s.skill_type === 'OFFER');
  const wanted = mySkills.filter((s) => s.skill_type === 'WANT');

  const myFirstTeach = offered[0]?.skill?.name || offered[0]?.name || 'Python';
  const myFirstLearn = wanted[0]?.skill?.name || wanted[0]?.name || 'Figma';

  // Check if candidate offers what user wants, or wants what user teaches
  const candOffered = (featuredCandidate?.skillsOffered || featuredCandidate?.skills_offered || []).map((s) =>
    typeof s === 'string' ? s : s.name
  );
  const candWanted = (featuredCandidate?.skillsWanted || featuredCandidate?.skills_wanted || []).map((s) =>
    typeof s === 'string' ? s : s.name
  );

  const matchedLearn = candOffered.find((c) => wanted.some((w) => (w.skill?.name || w.name || '').toLowerCase() === c.toLowerCase())) || myFirstLearn;
  const matchedTeach = candWanted.find((c) => offered.some((o) => (o.skill?.name || o.name || '').toLowerCase() === c.toLowerCase())) || myFirstTeach;

  return (
    <div className="bg-gradient-to-r from-slate-50 via-blue-50/40 to-indigo-50/40 rounded-3xl p-5 border border-slate-200/80">
      <div className="flex items-center justify-between mb-3.5">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-blue-600" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
            How Your Match Works
          </h4>
        </div>
        <span className="text-[11px] font-semibold text-blue-600 bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-100">
          2-Way Mutual Exchange
        </span>
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-6 py-2">
        {/* Step 1: Learning match */}
        <div className="flex items-center gap-2.5 bg-white px-4 py-2.5 rounded-2xl border border-slate-200/90 shadow-2xs">
          <div className="text-center">
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">You Want</span>
            <span className="block text-xs font-bold text-blue-700">{matchedLearn}</span>
          </div>

          <ArrowUpDown className="w-4 h-4 text-emerald-600 shrink-0" />

          <div className="text-center">
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">They Offer</span>
            <span className="block text-xs font-bold text-emerald-700">{matchedLearn}</span>
          </div>
        </div>

        {/* Plus sign */}
        <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center shrink-0">
          <Plus className="w-3.5 h-3.5" />
        </div>

        {/* Step 2: Teaching match */}
        <div className="flex items-center gap-2.5 bg-white px-4 py-2.5 rounded-2xl border border-slate-200/90 shadow-2xs">
          <div className="text-center">
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">You Offer</span>
            <span className="block text-xs font-bold text-emerald-700">{matchedTeach}</span>
          </div>

          <ArrowUpDown className="w-4 h-4 text-blue-600 shrink-0" />

          <div className="text-center">
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">They Want</span>
            <span className="block text-xs font-bold text-blue-700">{matchedTeach}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
