import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PlusCircle, Sparkles, CheckCircle2, Clock, MapPin, BookOpen, Send, AlertCircle } from 'lucide-react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { useAuth } from '../context/AuthContext';

export default function PostSwapPage() {
  const navigate = useNavigate();
  const { profile, offeredSkills = [], loading } = useAuth();

  const initialOfferSkill = offeredSkills[0]?.skill_name || offeredSkills[0]?.skill?.name || '';
  const initialAvailability = profile?.availability || 'Weekday afternoons';
  const initialLocation = profile?.location || profile?.college || profile?.university || 'Campus / Online';

  const [form, setForm] = useState({
    title: '',
    wantSkill: '',
    offerSkill: initialOfferSkill,
    category: 'coding',
    details: '',
    availability: initialAvailability,
    location: initialLocation
  });

  const [submitted, setSubmitted] = useState(false);

  // Sync initial values safely if profile or offeredSkills load asynchronously
  useEffect(() => {
    setForm(prev => ({
      ...prev,
      offerSkill: prev.offerSkill || offeredSkills[0]?.skill_name || offeredSkills[0]?.skill?.name || '',
      availability: prev.availability || profile?.availability || 'Weekday afternoons',
      location: prev.location || profile?.location || profile?.college || profile?.university || 'Campus / Online'
    }));
  }, [profile, offeredSkills]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => {
      navigate('/app/explore');
    }, 1800);
  };

  const hasNoOfferedSkills = !loading && offeredSkills.length === 0;

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-blue-600 font-semibold text-xs uppercase tracking-wider mb-1">
          <Sparkles className="w-4 h-4" /> Peer Exchange Marketplace
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
          Post a Skill Swap Request
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Share what skill you need help with and what you can teach in exchange to get matched with students on campus.
        </p>
      </div>

      {hasNoOfferedSkills ? (
        <Card className="p-8 text-center space-y-4 bg-amber-50/60 border-amber-200">
          <div className="w-14 h-14 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center mx-auto shadow-xs">
            <AlertCircle className="w-7 h-7" />
          </div>
          <h2 className="text-xl font-bold text-slate-900">You haven't added any skills to teach yet.</h2>
          <p className="text-xs text-slate-600 max-w-md mx-auto">
            Add a skill to your profile before creating a swap request.
          </p>
          <div className="pt-2 flex justify-center gap-3">
            <Button variant="primary" size="md" onClick={() => navigate('/app/profile/setup')}>
              Add Skill in Setup
            </Button>
            <Button variant="outline" size="md" onClick={() => navigate('/app/profile')}>
              Go to Profile
            </Button>
          </div>
        </Card>
      ) : submitted ? (
        <Card className="p-8 text-center space-y-4 bg-emerald-50/50 border-emerald-200">
          <div className="w-16 h-16 bg-emerald-500 text-white rounded-2xl flex items-center justify-center mx-auto shadow-lg shadow-emerald-500/20">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900">Skill Swap Request Posted!</h2>
          <p className="text-sm text-slate-600 max-w-md mx-auto">
            Your request has been published to the SkillSwap AI marketplace. We will notify you as soon as compatible students respond!
          </p>
          <div className="pt-2">
            <Button variant="primary" size="md" onClick={() => navigate('/app/explore')}>
              View Marketplace
            </Button>
          </div>
        </Card>
      ) : (
        <Card className="shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Post Title */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Post Title / Headline <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                required
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                placeholder="e.g. Looking for Figma mentor for Portfolio site in exchange for React tutoring"
                className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500"
              />
            </div>

            {/* Grid for Want & Offer Skills */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {/* What do you want to learn? */}
              <div className="p-4 bg-emerald-50/40 rounded-2xl border border-emerald-100/80 space-y-2">
                <label className="block text-xs font-bold text-emerald-800 uppercase tracking-wider flex items-center gap-1.5">
                  <BookOpen className="w-4 h-4 text-emerald-600" /> What do you want to learn? <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={form.wantSkill}
                  onChange={(e) => setForm({ ...form, wantSkill: e.target.value })}
                  placeholder="e.g. Figma UI Design, Machine Learning..."
                  className="w-full px-3.5 py-2 bg-white text-slate-900 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                />
              </div>

              {/* What can you offer? */}
              <div className="p-4 bg-blue-50/40 rounded-2xl border border-blue-100/80 space-y-2">
                <label className="block text-xs font-bold text-blue-800 uppercase tracking-wider flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-blue-600" /> What can you offer in return? <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={form.offerSkill}
                  onChange={(e) => setForm({ ...form, offerSkill: e.target.value })}
                  placeholder="e.g. React.js, Python, Spanish..."
                  className="w-full px-3.5 py-2 bg-white text-slate-900 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Details & Description */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Details & Learning Goals <span className="text-rose-500">*</span>
              </label>
              <textarea
                rows={4}
                required
                value={form.details}
                onChange={(e) => setForm({ ...form, details: e.target.value })}
                placeholder="Describe your current skill level, project goals, and what a 1-on-1 session would look like..."
                className="w-full p-4 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500"
              />
            </div>

            {/* Grid for Availability & Location */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {/* Availability */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-slate-400" /> Availability
                </label>
                <input
                  type="text"
                  value={form.availability}
                  onChange={(e) => setForm({ ...form, availability: e.target.value })}
                  placeholder="e.g. Mon & Wed 4-7 PM, Weekends"
                  className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500"
                />
              </div>

              {/* Location */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" /> Preferred Location
                </label>
                <input
                  type="text"
                  value={form.location}
                  onChange={(e) => setForm({ ...form, location: e.target.value })}
                  placeholder="e.g. Green Library / Zoom / Online"
                  className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Submit Button */}
            <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
              <Button
                variant="outline"
                size="lg"
                onClick={() => navigate('/app')}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                size="lg"
                type="submit"
                icon={Send}
              >
                Post Swap Request
              </Button>
            </div>
          </form>
        </Card>
      )}
    </div>
  );
}
