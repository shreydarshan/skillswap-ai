import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Users,
  Compass,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/auth';
import SearchBar from '../components/common/SearchBar';
import FeaturedMatchCard from '../components/profile/FeaturedMatchCard';
import RecommendedMatchCard from '../components/profile/RecommendedMatchCard';
import PersonalSkillSnapshot from '../components/dashboard/PersonalSkillSnapshot';
import QuickActions from '../components/dashboard/QuickActions';
import ReciprocalExplainer from '../components/dashboard/ReciprocalExplainer';
import Card from '../components/common/Card';
import Button from '../components/common/Button';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [mySkills, setMySkills] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [swapToast, setSwapToast] = useState(null);
  const [showAllMatches, setShowAllMatches] = useState(false);

  // Dynamic greeting based on user local time
  const hour = new Date().getHours();
  const timeGreeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
  const firstName = user?.full_name ? user.full_name.split(' ')[0] : 'Student';

  useEffect(() => {
    async function loadDashboardData() {
      setLoading(true);
      try {
        const [recsData, skillsData] = await Promise.all([
          authService.getHybridRecommendations().catch((err) => {
            console.warn('Failed to load hybrid recommendations:', err);
            return [];
          }),
          authService.getMySkills().catch(() => []),
        ]);

        setRecommendations(Array.isArray(recsData) ? recsData : []);
        setMySkills(Array.isArray(skillsData) ? skillsData : []);
      } catch (err) {
        console.warn('Dashboard loading error:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  // Determine user skill profile completeness
  const offeredCount = mySkills.filter((s) => s.skill_type === 'OFFER').length;
  const wantedCount = mySkills.filter((s) => s.skill_type === 'WANT').length;
  const isProfileReady = offeredCount > 0 && wantedCount > 0;

  // Deduplicate candidates by unique ID & exclude authenticated user / test accounts
  const seenIds = new Set();
  const uniqueCandidates = [];
  for (const c of recommendations) {
    const candId = c.candidate_id || c.user_id || c.id;
    if (!candId) continue;
    if (candId === user?.id || c.email === user?.email) continue;
    if (c.is_test || (c.email && c.email.includes('test_'))) continue;
    if (seenIds.has(candId)) continue;
    seenIds.add(candId);
    uniqueCandidates.push(c);
  }

  // RECOMMENDATIONS PURPOSE (Stage 7 & Stage 8):
  // Show only meaningful candidates with positive compatibility score > 0.
  // Hide 0% match cards from the Recommendations page.
  const meaningfulCandidates = uniqueCandidates.filter((candidate) => {
    const pct = candidate.hybrid_match_percentage !== undefined
      ? candidate.hybrid_match_percentage
      : (candidate.match_percentage !== undefined
        ? candidate.match_percentage
        : Math.round((candidate.hybrid_score || candidate.reciprocal_score || 0) * 100));
    return pct > 0;
  });

  // Filter recommendations based on local dashboard search query
  const filteredCandidates = meaningfulCandidates.filter((candidate) => {
    const candName = candidate.candidate_name || candidate.name || candidate.full_name || '';
    const skillsOff = (candidate.skillsOffered || candidate.skills_offered || []).map((s) =>
      typeof s === 'string' ? s : s.name
    );
    const skillsWnt = (candidate.skillsWanted || candidate.skills_wanted || []).map((s) =>
      typeof s === 'string' ? s : s.name
    );

    const q = searchQuery.toLowerCase().trim();
    if (!q) return true;

    return (
      candName.toLowerCase().includes(q) ||
      skillsOff.some((s) => s.toLowerCase().includes(q)) ||
      skillsWnt.some((s) => s.toLowerCase().includes(q))
    );
  });

  // Segregate into Featured (#1) and Top Matches (#2, #3, #4...)
  const featuredCandidate = filteredCandidates[0] || null;
  const secondaryCandidates = filteredCandidates.slice(1);
  const displayedSecondary = showAllMatches ? secondaryCandidates : secondaryCandidates.slice(0, 3);

  const handleSwapSuccess = (targetUser, offer, want) => {
    setSwapToast(`Swap request sent to ${targetUser.name || targetUser.full_name} (${offer} ↔ ${want})!`);
    setTimeout(() => setSwapToast(null), 4000);
  };

  return (
    <div className="space-y-6 sm:space-y-7 animate-in fade-in duration-300">
      {/* Toast Notification */}
      {swapToast && (
        <div className="fixed top-20 right-6 z-50 bg-slate-900 text-white px-4 py-3 rounded-2xl shadow-2xl border border-slate-800 flex items-center gap-3 animate-in slide-in-from-top-4 duration-200">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <span className="text-xs font-semibold">{swapToast}</span>
        </div>
      )}

      {/* TOP HEADER — Clean, Minimal, Personalized Greeting */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            {timeGreeting}, {firstName} 👋
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1 font-medium">
            Find someone to learn from — and something to teach back.
          </p>
        </div>

        {/* Local Dashboard Search */}
        <div className="w-full md:w-80">
          <SearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Search students, skills..."
          />
        </div>
      </div>

      {/* Profile Readiness Banner (Only shown if skills are missing) */}
      {!loading && !isProfileReady && (
        <Card className="bg-amber-50/80 border border-amber-200/90 shadow-2xs p-4 sm:p-5 rounded-3xl">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-amber-100 text-amber-800 rounded-xl shrink-0 mt-0.5">
                <AlertCircle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-sm sm:text-base">
                  Complete your skill profile to unlock personalized recommendations
                </h3>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  Add at least one skill you can teach and one skill you want to learn so our recommendation engine can find compatible partners for you.
                </p>
              </div>
            </div>

            <Button
              variant="primary"
              size="md"
              onClick={() => navigate('/app/profile')}
              className="shrink-0 text-xs font-bold px-4 py-2"
            >
              Update Skills
            </Button>
          </div>
        </Card>
      )}

      {/* PERSONAL SKILL SNAPSHOT */}
      <PersonalSkillSnapshot mySkills={mySkills} />

      {/* QUICK ACTIONS */}
      <QuickActions />

      {/* LOADING STATE */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center text-center">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-3" />
          <h3 className="font-bold text-slate-800 text-base">Finding your best skill partners...</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm">
            Calculating hybrid compatibility across reciprocal skills and student interaction history.
          </p>
        </div>
      ) : filteredCandidates.length === 0 ? (
        /* COMPACT, FRIENDLY EMPTY STATE */
        <div className="bg-white rounded-3xl p-8 sm:p-10 border border-slate-200/90 text-center max-w-xl mx-auto shadow-2xs">
          <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-4 border border-blue-100 shadow-2xs">
            <Sparkles className="w-7 h-7" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 mb-1">
            No strong matches yet
          </h3>
          <p className="text-xs sm:text-sm text-slate-500 mb-6 leading-relaxed">
            Add a skill you want to learn or a skill you can teach to discover reciprocal partners, or browse the campus community.
          </p>
          <div className="flex items-center justify-center gap-3">
            <Button
              variant="outline"
              size="md"
              onClick={() => navigate('/app/profile')}
              className="text-xs font-semibold"
            >
              Update My Skills
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={() => navigate('/app/explore')}
              className="text-xs font-semibold"
            >
              Explore Students
            </Button>
          </div>
        </div>
      ) : (
        /* DASHBOARD RECOMMENDATIONS CONTENT */
        <div className="space-y-6 sm:space-y-7">
          {/* 1. BEST MATCH (ONE PROMINENT FEATURED CARD) */}
          {featuredCandidate && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-base sm:text-lg font-bold text-slate-900 flex items-center gap-2">
                  <span>Best Match</span>
                </h2>
              </div>
              <FeaturedMatchCard
                candidate={featuredCandidate}
                onSwapSuccess={handleSwapSuccess}
              />
            </div>
          )}

          {/* 2. TOP MATCHES (COMPACT 3 MINI CARDS) */}
          {secondaryCandidates.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-base sm:text-lg font-bold text-slate-900 flex items-center gap-2">
                    <span>Top Matches for You</span>
                    <span className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs font-semibold rounded-full border border-blue-100">
                      {secondaryCandidates.length} Available
                    </span>
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Other compatible peers who share reciprocal skills with you.
                  </p>
                </div>

                <button
                  onClick={() => navigate('/app/explore')}
                  className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1 cursor-pointer"
                >
                  <span>Explore Community</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
                {displayedSecondary.map((candidate) => (
                  <RecommendedMatchCard
                    key={candidate.candidate_id || candidate.user_id || candidate.id}
                    candidate={candidate}
                    onSwapSuccess={handleSwapSuccess}
                  />
                ))}
              </div>

              {/* View all matches toggle if > 3 secondary matches exist */}
              {secondaryCandidates.length > 3 && (
                <div className="mt-5 text-center">
                  <button
                    onClick={() => setShowAllMatches(!showAllMatches)}
                    className="inline-flex items-center gap-1.5 px-4 py-2 bg-white hover:bg-slate-50 border border-slate-200 text-xs font-bold text-slate-700 rounded-full shadow-2xs transition-colors cursor-pointer"
                  >
                    <span>{showAllMatches ? 'Show Fewer Matches' : `View All ${secondaryCandidates.length} Matches`}</span>
                    {showAllMatches ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* 3. HOW YOUR MATCH WORKS (CONCISE VISUAL EXPLAINER) */}
          <ReciprocalExplainer mySkills={mySkills} featuredCandidate={featuredCandidate} />
        </div>
      )}
    </div>
  );
}
