import React, { useState } from 'react';
import { X, Send, Sparkles, Check, AlertCircle } from 'lucide-react';
import Button from '../common/Button';
import ProfileAvatar from '../profile/ProfileAvatar';
import { useAuth } from '../../context/AuthContext';
import { authService } from '../../services/auth';

export default function SwapRequestModal({ user, isOpen, onClose, onSuccess }) {
  const { user: currentUser, offeredSkills = [] } = useAuth();
  if (!isOpen || !user) return null;

  const defaultOffered = offeredSkills[0]?.skill_name || offeredSkills[0]?.skill?.name || 'General Mentorship';
  const [offeredSkill, setOfferedSkill] = useState(defaultOffered);
  const [requestedSkill, setRequestedSkill] = useState(user.skillsOffered?.[0]?.name || user.skills_offered?.[0] || '');
  const [message, setMessage] = useState(
    `Hi ${user.name}! I'd love to swap my ${offeredSkill} skills for your guidance in ${requestedSkill}. Let me know if you're free to connect!`
  );
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    const targetId = user.id || user.user_id || user.candidate_id;
    if (!targetId) {
      setError('Could not identify target student recipient.');
      return;
    }

    if (currentUser?.id && targetId === currentUser.id) {
      setError('You cannot send a skill swap request to yourself.');
      return;
    }

    setSubmitting(true);
    try {
      await authService.sendSwapRequest({
        receiverId: targetId,
        skillOfferedName: offeredSkill,
        skillRequestedName: requestedSkill,
        message
      });
      setSubmitted(true);
      setTimeout(() => {
        setSubmitted(false);
        onClose();
        if (onSuccess) onSuccess(user, offeredSkill, requestedSkill);
      }, 1500);
    } catch (err) {
      setError(err.message || 'Failed to send swap request. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-white w-full max-w-lg rounded-2xl border border-slate-200 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <ProfileAvatar
              src={user.avatar || user.avatar_url}
              name={user.name}
              email={user.email}
              genderPreference={user.gender_preference}
              size="sm"
            />
            <div>
              <h3 className="font-bold text-slate-900 text-base">Request Skill Swap</h3>
              <p className="text-xs text-slate-500">Propose a learning exchange with {user.name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {submitted ? (
          <div className="p-8 text-center space-y-3">
            <div className="w-14 h-14 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto shadow-xs">
              <Check className="w-7 h-7 stroke-[3]" />
            </div>
            <h4 className="text-lg font-bold text-slate-900">Request Sent Successfully!</h4>
            <p className="text-xs text-slate-500 max-w-xs mx-auto">
              We notified {user.name}. You will be alerted as soon as they accept your request.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {error && (
              <div className="p-3 bg-rose-50 text-rose-700 border border-rose-200 rounded-xl flex items-center gap-2 text-xs font-semibold animate-in fade-in">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-500" />
                <span>{error}</span>
              </div>
            )}

            {/* What you offer */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Skill You Will Teach / Offer
              </label>
              {offeredSkills.length > 0 ? (
                <select
                  value={offeredSkill}
                  onChange={(e) => setOfferedSkill(e.target.value)}
                  className="w-full px-3 py-2 bg-white text-slate-900 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                >
                  {offeredSkills.map((sk) => (
                    <option key={sk.id || sk.skill_id} value={sk.skill?.name || sk.skill_name}>
                      {sk.skill?.name || sk.skill_name} ({sk.proficiency_level})
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  type="text"
                  value={offeredSkill}
                  onChange={(e) => setOfferedSkill(e.target.value)}
                  placeholder="e.g. React.js, Python..."
                  className="w-full px-3 py-2 bg-white text-slate-900 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                />
              )}
            </div>

            {/* What you want */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Skill You Want to Learn from {user.name}
              </label>
              <select
                value={requestedSkill}
                onChange={(e) => setRequestedSkill(e.target.value)}
                className="w-full px-3 py-2 bg-white text-slate-900 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              >
                {user.skillsOffered?.map((sk) => (
                  <option key={sk.id} value={sk.name}>
                    {sk.name} ({sk.level})
                  </option>
                ))}
              </select>
            </div>

            {/* Introductory message */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Personalized Invitation Message
              </label>
              <textarea
                rows={3}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="w-full p-3 bg-white text-slate-900 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>

            {/* Footer Buttons */}
            <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-3">
              <Button variant="outline" size="md" onClick={onClose} disabled={submitting}>
                Cancel
              </Button>
              <Button variant="primary" size="md" type="submit" icon={Send} disabled={submitting}>
                {submitting ? 'Sending Request...' : 'Send Swap Request'}
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
