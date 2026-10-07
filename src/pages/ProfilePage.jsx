import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Star,
  MapPin,
  Award,
  BookOpen,
  Clock,
  Plus,
  Edit3,
  Check,
  Trash2,
  AlertCircle,
  LogOut
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/auth';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import SkillTag from '../components/common/SkillTag';
import ProfileAvatar from '../components/profile/ProfileAvatar';
import AvatarSelector from '../components/profile/AvatarSelector';
import { getAvatarUrl } from '../utils/avatar';

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user, profile: authProfile, refreshProfile, logout } = useAuth();

  const [profileData, setProfileData] = useState({
    full_name: '',
    bio: '',
    college: '',
    branch: '',
    year: '',
    location: '',
    experience_level: '',
    availability: '',
    gender_preference: ''
  });

  const [mySkills, setMySkills] = useState([]);
  const [isEditingBio, setIsEditingBio] = useState(false);
  const [newSkillOffered, setNewSkillOffered] = useState('');
  const [newSkillWanted, setNewSkillWanted] = useState('');
  const [toastMsg, setToastMsg] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load real profile & skills from FastAPI backend
  useEffect(() => {
    async function loadProfileAndSkills() {
      try {
        const prof = await authService.getMyProfile();
        if (prof) {
          setProfileData({
            full_name: prof.full_name || user?.full_name || '',
            bio: prof.bio || '',
            college: prof.college || '',
            branch: prof.branch || '',
            year: prof.year || '',
            location: prof.location || '',
            experience_level: prof.experience_level || '',
            availability: prof.availability || '',
            gender_preference: prof.gender_preference || '',
            avatar_url: prof.avatar_url || null
          });
        }
        const skillsList = await authService.getMySkills();
        setMySkills(skillsList || []);
      } catch (err) {
        console.warn('Could not load real profile data:', err);
      } finally {
        setLoading(false);
      }
    }

    if (user) {
      loadProfileAndSkills();
    }
  }, [user]);

  const handleSaveProfile = async (e) => {
    if (e) e.preventDefault();
    try {
      const updated = await authService.updateMyProfile(profileData);
      setProfileData({
        full_name: updated.full_name || '',
        bio: updated.bio || '',
        college: updated.college || '',
        branch: updated.branch || '',
        year: updated.year || '',
        location: updated.location || '',
        experience_level: updated.experience_level || '',
        availability: updated.availability || '',
        gender_preference: updated.gender_preference || '',
        avatar_url: updated.avatar_url || null
      });
      setIsEditingBio(false);
      await refreshProfile();
      showToast('Profile updated successfully!');
    } catch (err) {
      showToast('Error saving profile: ' + err.message);
    }
  };

  const handleAddSkill = async (e, skillName, skillType) => {
    e.preventDefault();
    if (!skillName.trim()) return;
    try {
      const added = await authService.addMySkill(skillName.trim(), skillType, 4);
      setMySkills((prev) => [...prev.filter((s) => s.id !== added.id), added]);
      if (skillType === 'OFFER') setNewSkillOffered('');
      else setNewSkillWanted('');
      showToast(`Added skill: ${skillName}`);
    } catch (err) {
      showToast('Error adding skill: ' + err.message);
    }
  };

  const handleRemoveSkill = async (userSkillId) => {
    try {
      await authService.removeMySkill(userSkillId);
      setMySkills((prev) => prev.filter((s) => s.id !== userSkillId));
      showToast('Skill removed');
    } catch (err) {
      showToast('Error removing skill: ' + err.message);
    }
  };

  const showToast = (msg) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3000);
  };

  const offeredSkills = mySkills.filter((s) => s.skill_type === 'OFFER');
  const wantedSkills = mySkills.filter((s) => s.skill_type === 'WANT');

  const displayName = profileData.full_name || user?.email || 'User';
  const initialLetter = displayName.charAt(0).toUpperCase();

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-300">
      {/* Toast Notification */}
      {toastMsg && (
        <div className="fixed top-20 right-6 z-50 bg-slate-900 text-white px-4 py-3 rounded-2xl shadow-2xl border border-slate-800 flex items-center gap-3">
          <Check className="w-5 h-5 text-emerald-400 shrink-0" />
          <span className="text-xs font-semibold">{toastMsg}</span>
        </div>
      )}

      {/* Cover Banner & Profile Card */}
      <div className="bg-white rounded-3xl border border-slate-200/90 shadow-sm overflow-hidden">
        {/* Subtle, Low-Contrast Accent Header - No giant saturated blue rectangle */}
        <div className="h-28 sm:h-36 bg-gradient-to-r from-slate-50 via-blue-50/40 to-indigo-50/50 border-b border-slate-100 relative">
          <div className="absolute inset-0 bg-[radial-gradient(#3b82f6_1px,transparent_1px)] [background-size:16px_16px] opacity-10 pointer-events-none" />
        </div>

        {/* Profile Content Header */}
        <div className="px-6 sm:px-8 pb-6 pt-0 relative">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between -mt-14 sm:-mt-16 mb-5 gap-4">
            <div className="flex flex-col sm:flex-row sm:items-end gap-5">
              <ProfileAvatar
                src={authProfile?.avatar_url || profileData.avatar_url}
                name={displayName}
                email={user?.email}
                genderPreference={profileData.gender_preference || authProfile?.gender_preference}
                size="2xl"
                className="border-4 border-white shadow-md bg-white rounded-3xl"
              />
              <div className="space-y-1 pb-1">
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                    {displayName}
                  </h1>
                </div>
                <p className="text-sm font-semibold text-slate-600">
                  {profileData.branch ? profileData.branch : 'Branch not set'}{' '}
                  {profileData.year ? `• Year ${profileData.year}` : ''}
                </p>
                <div className="flex items-center gap-4 text-xs text-slate-500 pt-0.5">
                  <span className="flex items-center gap-1.5 font-medium">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    {profileData.college || 'College not set'}{' '}
                    {profileData.location ? `(${profileData.location})` : ''}
                  </span>
                </div>
              </div>
            </div>

            <div className="sm:self-end pb-1 flex items-center gap-2 flex-wrap">
              <Button
                variant="outline"
                size="md"
                icon={Edit3}
                onClick={() => setIsEditingBio(!isEditingBio)}
              >
                {isEditingBio ? 'Cancel' : 'Edit Profile'}
              </Button>
              <Button
                variant="outline"
                size="md"
                icon={LogOut}
                onClick={() => {
                  logout();
                  navigate('/login');
                }}
                className="text-slate-500 hover:text-rose-600 hover:bg-rose-50 border-slate-200"
              >
                Log Out
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Profile Editing Form */}
      {isEditingBio && (
        <Card className="p-6 space-y-4 bg-blue-50/40 border-blue-200">
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
            Edit Profile Details
          </h3>
          <form onSubmit={handleSaveProfile} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Full Name</label>
                <input
                  type="text"
                  value={profileData.full_name}
                  onChange={(e) => setProfileData({ ...profileData, full_name: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">College / University</label>
                <input
                  type="text"
                  value={profileData.college}
                  onChange={(e) => setProfileData({ ...profileData, college: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Branch / Major</label>
                <input
                  type="text"
                  value={profileData.branch}
                  onChange={(e) => setProfileData({ ...profileData, branch: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Year of Study</label>
                <input
                  type="number"
                  min={1}
                  max={6}
                  value={profileData.year}
                  onChange={(e) => setProfileData({ ...profileData, year: parseInt(e.target.value) || 1 })}
                  className="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-sm"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Bio / Summary</label>
              <textarea
                rows={3}
                value={profileData.bio}
                onChange={(e) => setProfileData({ ...profileData, bio: e.target.value })}
                placeholder="Share a brief overview of your academic goals & skills..."
                className="w-full p-3 bg-white border border-slate-200 rounded-xl text-sm"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Availability</label>
                <input
                  type="text"
                  value={profileData.availability}
                  onChange={(e) => setProfileData({ ...profileData, availability: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Location</label>
                <input
                  type="text"
                  value={profileData.location}
                  onChange={(e) => setProfileData({ ...profileData, location: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-sm"
                />
              </div>

              <div className="sm:col-span-2">
                <AvatarSelector
                  value={profileData.gender_preference || ''}
                  onChange={(pref, photoUrl) =>
                    setProfileData({
                      ...profileData,
                      gender_preference: pref,
                      avatar_url: photoUrl,
                    })
                  }
                  name={displayName}
                  email={user?.email}
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="ghost" size="sm" onClick={() => setIsEditingBio(false)}>
                Cancel
              </Button>
              <Button type="submit" variant="primary" size="sm">
                Save Profile
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* Bio Display */}
      {!isEditingBio && (
        <Card>
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-2">
            About Me / Student Bio
          </h3>
          <p className="text-sm text-slate-600 leading-relaxed">
            {profileData.bio || "No bio added yet. Click 'Edit Profile' to introduce yourself to peers."}
          </p>
        </Card>
      )}

      {/* Skills Offered & Skills Wanted Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Skills Offered */}
        <Card className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-blue-700 uppercase tracking-wider flex items-center gap-1.5">
              <Award className="w-4 h-4 text-blue-600" /> Skills I Offer / Teach
            </h3>
          </div>

          <div className="flex flex-wrap gap-2">
            {offeredSkills.map((sk) => (
              <div key={sk.id} className="inline-flex items-center gap-1">
                <SkillTag name={sk.skill_name || 'Skill'} variant="offer" badge={`Lvl ${sk.proficiency}`} />
                <button
                  onClick={() => handleRemoveSkill(sk.id)}
                  className="text-slate-400 hover:text-rose-500 p-0.5 rounded-full hover:bg-rose-50"
                  title="Remove skill"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
            {offeredSkills.length === 0 && (
              <p className="text-xs text-slate-400 italic">No offered skills added yet.</p>
            )}
          </div>

          <form onSubmit={(e) => handleAddSkill(e, newSkillOffered, 'OFFER')} className="pt-2 flex items-center gap-2">
            <input
              type="text"
              value={newSkillOffered}
              onChange={(e) => setNewSkillOffered(e.target.value)}
              placeholder="Add skill to offer (e.g. React.js)..."
              className="flex-1 px-3 py-1.5 bg-slate-50 border border-slate-200 text-xs rounded-xl focus:bg-white focus:outline-none focus:border-blue-500"
            />
            <Button type="submit" variant="secondary" size="sm" icon={Plus}>
              Add
            </Button>
          </form>
        </Card>

        {/* Skills Wanted */}
        <Card className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-emerald-700 uppercase tracking-wider flex items-center gap-1.5">
              <BookOpen className="w-4 h-4 text-emerald-600" /> Skills I Want to Learn
            </h3>
          </div>

          <div className="flex flex-wrap gap-2">
            {wantedSkills.map((sk) => (
              <div key={sk.id} className="inline-flex items-center gap-1">
                <SkillTag name={sk.skill_name || 'Skill'} variant="want" badge={`Lvl ${sk.proficiency}`} />
                <button
                  onClick={() => handleRemoveSkill(sk.id)}
                  className="text-slate-400 hover:text-rose-500 p-0.5 rounded-full hover:bg-rose-50"
                  title="Remove skill"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
            {wantedSkills.length === 0 && (
              <p className="text-xs text-slate-400 italic">No learning goals added yet.</p>
            )}
          </div>

          <form onSubmit={(e) => handleAddSkill(e, newSkillWanted, 'WANT')} className="pt-2 flex items-center gap-2">
            <input
              type="text"
              value={newSkillWanted}
              onChange={(e) => setNewSkillWanted(e.target.value)}
              placeholder="Add skill to learn (e.g. Machine Learning)..."
              className="flex-1 px-3 py-1.5 bg-slate-50 border border-slate-200 text-xs rounded-xl focus:bg-white focus:outline-none focus:border-blue-500"
            />
            <Button type="submit" variant="secondary" size="sm" icon={Plus}>
              Add
            </Button>
          </form>
        </Card>
      </div>

      {/* Availability Card */}
      <Card>
        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-2 flex items-center gap-1.5">
          <Clock className="w-4 h-4 text-slate-500" /> Availability & Schedule
        </h3>
        <p className="text-sm text-slate-700 bg-slate-50 p-3.5 rounded-xl border border-slate-200/60 font-medium">
          {profileData.availability || "Not specified"}
        </p>
      </Card>
    </div>
  );
}
