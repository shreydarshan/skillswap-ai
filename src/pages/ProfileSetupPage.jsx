import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, User, GraduationCap, BookOpen, MapPin, Clock, Plus, CheckCircle2, AlertCircle } from 'lucide-react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import AvatarSelector from '../components/profile/AvatarSelector';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/auth';

export default function ProfileSetupPage() {
  const navigate = useNavigate();
  const { user, profile, refreshProfile, refreshSkills } = useAuth();

  const [fullName, setFullName] = useState(user?.full_name || profile?.full_name || '');
  const [college, setCollege] = useState(profile?.college || '');
  const [branch, setBranch] = useState(profile?.branch || '');
  const [year, setYear] = useState(profile?.year ? String(profile.year) : '');
  const [bio, setBio] = useState(profile?.bio || '');
  const [location, setLocation] = useState(profile?.location || '');
  const [availability, setAvailability] = useState(profile?.availability || '');
  const [genderPreference, setGenderPreference] = useState(profile?.gender_preference || '');
  const [avatarUrl, setAvatarUrl] = useState(profile?.avatar_url || null);

  const [offeredSkillName, setOfferedSkillName] = useState('');
  const [offeredProficiency, setOfferedProficiency] = useState(4);

  const [wantedSkillName, setWantedSkillName] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!fullName.trim() || !college.trim() || !branch.trim() || !year) {
      setError('Please fill in all required profile fields (Full Name, College, Branch, Year).');
      return;
    }

    if (!offeredSkillName.trim() || !wantedSkillName.trim()) {
      setError('Please add at least one skill you can teach and one skill you want to learn.');
      return;
    }

    setLoading(true);
    try {
      // 1. Update Profile
      await authService.updateMyProfile({
        full_name: fullName.trim(),
        college: college.trim(),
        branch: branch.trim(),
        year: parseInt(year, 10),
        bio: bio.trim() || null,
        location: location.trim() || null,
        availability: availability.trim() || null,
        gender_preference: genderPreference || null,
        avatar_url: avatarUrl || null
      });

      // 2. Add Offered Skill
      await authService.addMySkill(
        offeredSkillName.trim(),
        'OFFER',
        parseInt(offeredProficiency, 10),
        'General'
      );

      // 3. Add Wanted Skill
      await authService.addMySkill(
        wantedSkillName.trim(),
        'WANT',
        1,
        'General'
      );

      await refreshProfile();
      await refreshSkills();

      navigate('/app');
    } catch (err) {
      setError(err.message || 'Failed to complete profile setup. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 py-4 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 text-white rounded-3xl p-6 sm:p-8 shadow-xl">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/15 backdrop-blur-md rounded-full text-xs font-semibold text-blue-100 mb-3 border border-white/20">
          <Sparkles className="w-3.5 h-3.5 text-amber-300" />
          <span>Student Onboarding</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white mb-2">
          Welcome to SkillSwap AI!
        </h1>
        <p className="text-blue-100 text-xs sm:text-sm leading-relaxed">
          Complete your profile to start finding skill partners.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 text-rose-800 border border-rose-200 rounded-2xl flex items-center gap-3 text-xs font-semibold">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <Card className="shadow-sm">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Required Academic Info */}
          <div className="space-y-4">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <User className="w-4 h-4 text-blue-600" /> Required Student Info <span className="text-rose-500">*</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="sm:col-span-2">
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Full Name <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  autoComplete="off"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Jane Doe"
                  className="w-full px-3.5 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  College / University <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  autoComplete="off"
                  value={college}
                  onChange={(e) => setCollege(e.target.value)}
                  placeholder="e.g. Stanford University"
                  className="w-full px-3.5 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Branch / Major <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  autoComplete="off"
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  placeholder="e.g. Computer Science"
                  className="w-full px-3.5 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Year of Study <span className="text-rose-500">*</span>
                </label>
                <select
                  required
                  value={year}
                  onChange={(e) => setYear(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-white text-slate-900 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                >
                  <option value="">Select Year of Study</option>
                  <option value="1">1st Year (Freshman)</option>
                  <option value="2">2nd Year (Sophomore)</option>
                  <option value="3">3rd Year (Junior)</option>
                  <option value="4">4th Year (Senior)</option>
                  <option value="5">Graduate / Master's</option>
                  <option value="6">PhD Scholar</option>
                </select>
              </div>
            </div>
          </div>

          {/* Initial Skills Setup */}
          <div className="pt-4 border-t border-slate-100 space-y-4">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-emerald-600" /> Initial Skill Exchange Setup <span className="text-rose-500">*</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 bg-blue-50/50 rounded-2xl border border-blue-100 space-y-3">
                <label className="block text-xs font-bold text-blue-900 uppercase tracking-wider">
                  Skill You Can Teach <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  autoComplete="off"
                  value={offeredSkillName}
                  onChange={(e) => setOfferedSkillName(e.target.value)}
                  placeholder="e.g. Python, React.js, Spanish"
                  className="w-full px-3 py-2 bg-white text-slate-900 border border-slate-200 rounded-xl text-xs sm:text-sm"
                />
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                    Proficiency (1-5)
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="5"
                    value={offeredProficiency}
                    onChange={(e) => setOfferedProficiency(e.target.value)}
                    className="w-full accent-blue-600"
                  />
                  <span className="text-[10px] text-blue-700 font-bold block text-right">
                    Level: {offeredProficiency}/5
                  </span>
                </div>
              </div>

              <div className="p-4 bg-emerald-50/50 rounded-2xl border border-emerald-100 space-y-3">
                <label className="block text-xs font-bold text-emerald-900 uppercase tracking-wider">
                  Skill You Want to Learn <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  autoComplete="off"
                  value={wantedSkillName}
                  onChange={(e) => setWantedSkillName(e.target.value)}
                  placeholder="e.g. Figma UI/UX, Machine Learning"
                  className="w-full px-3 py-2 bg-white text-slate-900 border border-slate-200 rounded-xl text-xs sm:text-sm"
                />
                <p className="text-[10px] text-slate-500">
                  We use your learning goal to discover peer teachers on campus.
                </p>
              </div>
            </div>
          </div>

          {/* Recommended Info */}
          <div className="pt-4 border-t border-slate-100 space-y-4">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <GraduationCap className="w-4 h-4 text-indigo-600" /> Additional Details (Optional)
            </h3>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-slate-700 mb-1">Short Bio</label>
                <textarea
                  rows={2}
                  autoComplete="off"
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  placeholder="Brief description of your academic interests or learning goals..."
                  className="w-full p-3 bg-white border border-slate-200 rounded-xl text-xs text-slate-900"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block font-medium text-slate-700 mb-1">Campus Location</label>
                  <input
                    type="text"
                    autoComplete="off"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g. Main Library / On-Campus"
                    className="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs text-slate-900"
                  />
                </div>

                <div>
                  <label className="block font-medium text-slate-700 mb-1">Weekly Availability</label>
                  <input
                    type="text"
                    autoComplete="off"
                    value={availability}
                    onChange={(e) => setAvailability(e.target.value)}
                    placeholder="e.g. Mon & Wed 4-6 PM"
                    className="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs text-slate-900"
                  />
                </div>

                <div className="sm:col-span-2">
                  <AvatarSelector
                    value={genderPreference}
                    onChange={(pref, photoUrl) => {
                      setGenderPreference(pref);
                      setAvatarUrl(photoUrl);
                    }}
                    name={fullName}
                    email={user?.email}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Submit */}
          <div className="pt-4 border-t border-slate-100 flex items-center justify-end">
            <Button
              type="submit"
              variant="primary"
              size="lg"
              disabled={loading}
              icon={CheckCircle2}
            >
              {loading ? 'Saving Profile...' : 'Complete Profile Setup'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
