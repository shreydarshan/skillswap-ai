import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  Zap,
  CheckCircle2,
  Users,
  BookOpen,
  GraduationCap,
  Star,
  Cpu,
  Heart,
  Check,
  Award
} from 'lucide-react';
import Button from '../components/common/Button';
import Card from '../components/common/Card';
import SkillTag from '../components/common/SkillTag';
import MatchBadge from '../components/common/MatchBadge';
import { CURRENT_USER, MOCK_STUDENTS } from '../data/mockUsers';

export default function LandingPage() {
  const navigate = useNavigate();

  // Pick Marcus Vance as our featured demo match
  const featuredMatch = MOCK_STUDENTS[1];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900 selection:bg-blue-100 selection:text-blue-700">
      {/* Navbar */}
      <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div
            onClick={() => navigate('/')}
            className="flex items-center gap-2.5 cursor-pointer group"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-blue-500 text-white flex items-center justify-center shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform duration-200">
              <Zap className="w-5 h-5 fill-white" />
            </div>
            <div>
              <span className="font-bold text-xl text-slate-900 tracking-tight leading-none block">
                SkillSwap <span className="text-blue-600">AI</span>
              </span>
              <span className="text-[10px] text-slate-400 font-medium tracking-wide uppercase block">
                Student Skill Exchange
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button variant="ghost" size="md" onClick={() => navigate('/login')}>
              Log in
            </Button>
            <Button variant="primary" size="md" onClick={() => navigate('/signup')}>
              Get Started
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-16 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-center flex flex-col items-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-blue-50 text-blue-700 border border-blue-200/80 rounded-full text-xs font-semibold mb-6 shadow-2xs">
          <Sparkles className="w-4 h-4 text-blue-600" />
          <span>Student Skill Exchange & AI Recommendation System</span>
        </div>

        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-slate-900 max-w-4xl leading-[1.1] mb-6">
          Learn any skill on campus by <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-500">swapping what you know</span>.
        </h1>

        <p className="text-base sm:text-xl text-slate-600 max-w-2xl mx-auto mb-8 leading-relaxed">
          SkillSwap AI matches college students for 1-on-1 peer learning. Exchange coding, design, language, or math skills with verified peers—100% free.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full max-w-md">
          <Button
            variant="primary"
            size="lg"
            fullWidth
            onClick={() => navigate('/app')}
            icon={ArrowRight}
            iconPosition="right"
            className="shadow-lg shadow-blue-500/25 py-3.5 text-base font-bold"
          >
            Launch Recommendation App
          </Button>
          <Button
            variant="outline"
            size="lg"
            fullWidth
            onClick={() => navigate('/login')}
            className="py-3.5 text-base font-semibold"
          >
            Sign In with .edu
          </Button>
        </div>
      </section>

      {/* SECTION: "How SkillSwap finds your match" (Product Recommendation Pipeline) */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-indigo-50 text-indigo-700 font-bold text-xs uppercase tracking-wider rounded-full mb-3">
            <Cpu className="w-3.5 h-3.5 text-indigo-600" /> Recommendation Pipeline
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            How SkillSwap finds your match
          </h2>
          <p className="text-slate-600 text-sm sm:text-base mt-2">
            Our 2-way compatibility engine pairs your offered skills with peer requests to calculate high-accuracy reciprocal matches.
          </p>
        </div>

        {/* Visual Pipeline Flow */}
        <div className="bg-white rounded-3xl border border-slate-200/90 p-6 sm:p-10 shadow-xl relative overflow-hidden">
          {/* Header Step Pipeline Indicator */}
          <div className="hidden lg:grid grid-cols-3 gap-6 text-center text-xs font-bold text-slate-400 uppercase tracking-wider mb-8 pb-4 border-b border-slate-100">
            <div className="flex items-center justify-center gap-2 text-blue-600">
              <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs">1</span>
              <span>Your Student Profile</span>
            </div>
            <div className="flex items-center justify-center gap-2 text-indigo-600">
              <span className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-xs">2</span>
              <span>AI Recommendation Engine</span>
            </div>
            <div className="flex items-center justify-center gap-2 text-emerald-600">
              <span className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs">3</span>
              <span>Recommended Skill Partner</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
            {/* Step 1: Student Profile (Left Card) */}
            <div className="lg:col-span-4 bg-slate-50 rounded-2xl p-5 border border-slate-200 space-y-4">
              <div className="flex items-center gap-3">
                <img
                  src={CURRENT_USER.avatar}
                  alt={CURRENT_USER.name}
                  className="w-12 h-12 rounded-xl object-cover border border-white shadow-xs"
                />
                <div>
                  <h3 className="font-bold text-slate-900 text-sm">{CURRENT_USER.name}</h3>
                  <p className="text-xs text-slate-500">{CURRENT_USER.major}</p>
                  <span className="text-[10px] text-blue-600 font-semibold">{CURRENT_USER.university}</span>
                </div>
              </div>

              {/* Skills I Can Teach */}
              <div className="space-y-1.5">
                <span className="block text-[11px] font-bold text-blue-700 uppercase tracking-wider">
                  Skills I Can Teach:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  <SkillTag name="Python" variant="offer" size="sm" badge="Expert" />
                  <SkillTag name="React.js" variant="offer" size="sm" badge="Expert" />
                  <SkillTag name="Tailwind CSS" variant="offer" size="sm" badge="Advanced" />
                </div>
              </div>

              {/* Skills I Want to Learn */}
              <div className="space-y-1.5">
                <span className="block text-[11px] font-bold text-emerald-700 uppercase tracking-wider">
                  Skills I Want to Learn:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  <SkillTag name="Machine Learning" variant="want" size="sm" badge="High" />
                  <SkillTag name="Figma UI/UX" variant="want" size="sm" badge="Medium" />
                </div>
              </div>

              {/* Student Interests */}
              <div className="space-y-1.5 pt-1 border-t border-slate-200/60">
                <span className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                  Interests:
                </span>
                <div className="flex flex-wrap gap-1 text-[11px] text-slate-600">
                  <span className="px-2 py-0.5 bg-white border rounded-md">Artificial Intelligence</span>
                  <span className="px-2 py-0.5 bg-white border rounded-md">Web Dev</span>
                  <span className="px-2 py-0.5 bg-white border rounded-md">Mobile Apps</span>
                </div>
              </div>
            </div>

            {/* Step 2: AI Engine Connector (Middle Card) */}
            <div className="lg:col-span-3 flex flex-col items-center justify-center p-4 bg-gradient-to-br from-blue-600 via-indigo-600 to-blue-700 text-white rounded-2xl text-center space-y-3 shadow-lg shadow-blue-500/20">
              <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center text-white">
                <Cpu className="w-6 h-6 animate-pulse" />
              </div>

              <div className="space-y-1">
                <span className="px-2.5 py-0.5 bg-white/20 text-white rounded-full text-[10px] font-bold uppercase tracking-wider">
                  Reciprocal Matrix
                </span>
                <h4 className="font-bold text-base text-white">AI Recommendation Engine</h4>
                <p className="text-xs text-blue-100 leading-relaxed max-w-xs">
                  Analyzes 2-way skill overlap, timetable availability, and campus location proximity.
                </p>
              </div>

              <div className="pt-2 flex items-center justify-center text-amber-300 gap-1 text-xs font-semibold">
                <Sparkles className="w-4 h-4" />
                <span>2-Way Match Found!</span>
              </div>
            </div>

            {/* Step 3: Recommended Match Preview (Right Card) */}
            <div className="lg:col-span-5 bg-white rounded-2xl p-5 border-2 border-blue-500/30 shadow-md space-y-4 relative">
              {/* Header: Avatar + Match Badge */}
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <img
                    src={featuredMatch.avatar}
                    alt={featuredMatch.name}
                    className="w-12 h-12 rounded-xl object-cover border border-slate-200 shadow-xs"
                  />
                  <div>
                    <h3 className="font-bold text-slate-900 text-base">{featuredMatch.name}</h3>
                    <p className="text-xs text-slate-500">{featuredMatch.role}</p>
                    <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
                      <span className="text-blue-600 font-semibold">{featuredMatch.university}</span>
                      <span>•</span>
                      <span className="flex items-center gap-1 text-amber-600 font-semibold">
                        <Star className="w-3 h-3 fill-amber-400" /> {featuredMatch.rating}
                      </span>
                    </div>
                  </div>
                </div>

                <MatchBadge percentage={94} size="md" />
              </div>

              {/* Offered / Wanted Summary */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2 bg-blue-50/60 rounded-xl border border-blue-100">
                  <span className="text-[10px] font-bold text-blue-700 uppercase block mb-1">Teaches:</span>
                  <SkillTag name="Machine Learning" variant="offer" size="sm" />
                </div>
                <div className="p-2 bg-emerald-50/60 rounded-xl border border-emerald-100">
                  <span className="text-[10px] font-bold text-emerald-700 uppercase block mb-1">Wants:</span>
                  <SkillTag name="Python" variant="want" size="sm" />
                </div>
              </div>

              {/* "Why this match?" Explanation Section */}
              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/80 space-y-2">
                <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900">
                  <Sparkles className="w-4 h-4 text-blue-600" />
                  <span>Why this match?</span>
                </div>

                <div className="space-y-1.5 text-xs text-slate-700">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span>They teach <strong>Machine Learning</strong> (matches your goal)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span>You teach <strong>Python</strong> (matches their request)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span>They want to learn <strong>Python</strong></span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span>You want to learn <strong>Machine Learning</strong></span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span>Compatible availability (Weekdays 5-8 PM)</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-2 gap-2 pt-1">
                <Button variant="outline" size="sm" onClick={() => navigate('/app')}>
                  View Profile
                </Button>
                <Button variant="primary" size="sm" onClick={() => navigate('/app')}>
                  Request Swap
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION: "How it works" (3 Steps) */}
      <section className="py-16 bg-white border-y border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
              How it works
            </h2>
            <p className="text-slate-500 text-sm mt-2">
              Start swapping skills on campus in 3 simple steps
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="p-6 space-y-3 border-slate-200/80 text-center">
              <div className="w-12 h-12 bg-blue-100 text-blue-700 font-bold rounded-2xl flex items-center justify-center mx-auto text-lg">
                1
              </div>
              <h3 className="text-lg font-bold text-slate-900">Create your profile</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Sign in with your official .edu university email, enter your major, and specify your current year on campus.
              </p>
            </Card>

            <Card className="p-6 space-y-3 border-slate-200/80 text-center">
              <div className="w-12 h-12 bg-indigo-100 text-indigo-700 font-bold rounded-2xl flex items-center justify-center mx-auto text-lg">
                2
              </div>
              <h3 className="text-lg font-bold text-slate-900">Tell us what you want to learn & teach</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Add skills you excel at (e.g. React, Spanish, Calculus) and skills you want to learn this semester.
              </p>
            </Card>

            <Card className="p-6 space-y-3 border-slate-200/80 text-center">
              <div className="w-12 h-12 bg-emerald-100 text-emerald-700 font-bold rounded-2xl flex items-center justify-center mx-auto text-lg">
                3
              </div>
              <h3 className="text-lg font-bold text-slate-900">Get personalized skill-swap recommendations</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Connect with compatible peers, schedule 1-on-1 peer sessions, and exchange knowledge effortlessly.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* SECTION: "Why SkillSwap?" (4 Concise Cards) */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            Why SkillSwap?
          </h2>
          <p className="text-slate-500 text-sm mt-2">
            Designed specifically for college students seeking collaborative, peer-to-peer growth.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card hoverEffect className="p-6 space-y-3 border-slate-200/80">
            <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center">
              <Users className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900">Learn from peers</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Get 1-on-1 practical guidance from students who recently mastered the exact subject or course.
            </p>
          </Card>

          <Card hoverEffect className="p-6 space-y-3 border-slate-200/80">
            <div className="w-10 h-10 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center">
              <GraduationCap className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900">Teach what you know</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Reinforce your own knowledge and build your resume by tutoring fellow peers on campus.
            </p>
          </Card>

          <Card hoverEffect className="p-6 space-y-3 border-slate-200/80">
            <div className="w-10 h-10 bg-amber-50 text-amber-600 rounded-xl flex items-center justify-center">
              <Sparkles className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900">AI-powered matching</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Our 2-way compatibility matrix finds student partners with 90%+ reciprocal skill overlap.
            </p>
          </Card>

          <Card hoverEffect className="p-6 space-y-3 border-slate-200/80">
            <div className="w-10 h-10 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center">
              <Heart className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900">Completely free for students</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              No money involved. Exchange 1 hour of your teaching for 1 hour of personalized peer learning.
            </p>
          </Card>
        </div>
      </section>

      {/* SECTION: Bottom Call To Action */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto w-full">
        <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 text-white rounded-3xl p-8 sm:p-12 text-center shadow-xl shadow-blue-500/20 relative overflow-hidden">
          <div className="relative z-10 max-w-2xl mx-auto space-y-6">
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
              Ready to swap skills with peers on your campus?
            </h2>
            <p className="text-blue-100 text-sm sm:text-base leading-relaxed">
              Join students swapping Web Dev, Figma, Machine Learning, Languages, and Math right now.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <Button
                variant="secondary"
                size="lg"
                onClick={() => navigate('/app')}
                icon={ArrowRight}
                iconPosition="right"
                className="font-bold text-blue-700"
              >
                Launch Recommendation App
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-8 text-xs text-center border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 space-y-2">
          <p className="font-semibold text-slate-200">SkillSwap AI • Student Skill Exchange and Recommendation System</p>
          <p className="text-slate-500">Built with React, Vite, Tailwind CSS & React Router.</p>
        </div>
      </footer>
    </div>
  );
}
