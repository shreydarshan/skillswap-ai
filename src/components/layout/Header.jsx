import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bell,
  Search,
  Zap,
  Users,
  BookOpen,
  ArrowRight,
  GraduationCap,
  Sparkles,
  LogOut,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { authService } from '../../services/auth';
import { getAvatarUrl } from '../../utils/avatar';
import SearchBar from '../common/SearchBar';
import ProfileAvatar from '../profile/ProfileAvatar';

export default function Header() {
  const navigate = useNavigate();
  const { user, profile, logout } = useAuth();
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [allStudents, setAllStudents] = useState([]);

  const searchInputRef = useRef(null);
  const searchContainerRef = useRef(null);

  const displayName = user?.full_name || profile?.full_name || user?.email || 'Student User';
  const avatarUrl = getAvatarUrl(
    profile?.avatar_url,
    displayName,
    user?.email,
    profile?.gender_preference
  );
  const unreadCount = notifications.filter((n) => n.unread).length;

  // Keyboard shortcut: '/' focuses the search field anywhere on the page
  useEffect(() => {
    const handleGlobalKeyDown = (e) => {
      if (
        e.key === '/' &&
        !['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName) &&
        !e.ctrlKey &&
        !e.metaKey
      ) {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, []);

  // Click outside listener to close search suggestions & notifications
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch student directory once for instantaneous, lightweight search suggestions
  useEffect(() => {
    let isMounted = true;
    authService
      .getStudents()
      .then((data) => {
        if (isMounted && Array.isArray(data)) {
          setAllStudents(data);
        }
      })
      .catch(() => {});
    return () => {
      isMounted = false;
    };
  }, []);

  // Filter matching students & skills for live suggestions
  const trimmed = searchQuery.trim().toLowerCase();
  const matchingStudents = trimmed
    ? allStudents
        .filter((s) => {
          if (s.id === user?.id || s.email === user?.email) return false;
          const name = (s.name || '').toLowerCase();
          const univ = (s.university || s.college || '').toLowerCase();
          const role = (s.role || s.branch || '').toLowerCase();
          return name.includes(trimmed) || univ.includes(trimmed) || role.includes(trimmed);
        })
        .slice(0, 3)
    : [];

  const matchingSkills = trimmed
    ? Array.from(
        new Set(
          allStudents
            .flatMap((s) => [
              ...(s.skillsOffered || []).map((sk) => (typeof sk === 'string' ? sk : sk.name)),
              ...(s.skillsWanted || []).map((sk) => (typeof sk === 'string' ? sk : sk.name)),
            ])
            .filter((skName) => skName && skName.toLowerCase().includes(trimmed))
        )
      ).slice(0, 4)
    : [];

  const handleSearchSubmit = (query = searchQuery) => {
    const cleanQuery = query.trim();
    setShowSuggestions(false);
    if (cleanQuery) {
      navigate(`/app/explore?q=${encodeURIComponent(cleanQuery)}`);
    } else {
      navigate('/app/explore');
    }
  };

  const handleSelectSkillSuggestion = (skillName) => {
    setSearchQuery(skillName);
    setShowSuggestions(false);
    navigate(`/app/explore?q=${encodeURIComponent(skillName)}`);
  };

  const handleSelectStudentSuggestion = (student) => {
    setShowSuggestions(false);
    navigate(`/app/explore?q=${encodeURIComponent(student.name)}`);
  };

  return (
    <header className="sticky top-0 z-20 h-16 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-4">
      {/* Mobile Brand / Logo */}
      <div className="flex items-center gap-2.5 lg:hidden">
        <div
          onClick={() => navigate('/app')}
          className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center cursor-pointer shadow-xs hover:bg-blue-700 transition-colors"
        >
          <Zap className="w-4 h-4 fill-white" />
        </div>
        <span
          onClick={() => navigate('/app')}
          className="font-bold text-base text-slate-900 cursor-pointer tracking-tight"
        >
          SkillSwap <span className="text-blue-600">AI</span>
        </span>
      </div>

      {/* Global Functional Search Bar with Live Suggestions */}
      <div ref={searchContainerRef} className="flex-1 max-w-lg relative hidden sm:block">
        <SearchBar
          ref={searchInputRef}
          value={searchQuery}
          onChange={(val) => {
            setSearchQuery(val);
            setShowSuggestions(Boolean(val.trim()));
          }}
          onSubmit={handleSearchSubmit}
          onEscape={() => setShowSuggestions(false)}
          onFocus={() => {
            if (searchQuery.trim()) setShowSuggestions(true);
          }}
          placeholder="Search students, offered or wanted skills..."
        />

        {/* Live Search Suggestions Dropdown */}
        {showSuggestions && (matchingStudents.length > 0 || matchingSkills.length > 0) && (
          <div className="absolute left-0 right-0 top-full mt-2 bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden z-50 divide-y divide-slate-100 animate-in fade-in slide-in-from-top-1 duration-150">
            {/* Matching Skills */}
            {matchingSkills.length > 0 && (
              <div className="p-2.5">
                <span className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 px-2 py-1 flex items-center gap-1.5">
                  <BookOpen className="w-3 h-3 text-blue-600" /> Matching Skills
                </span>
                <div className="space-y-0.5 mt-1">
                  {matchingSkills.map((skName, i) => (
                    <button
                      key={i}
                      type="button"
                      onClick={() => handleSelectSkillSuggestion(skName)}
                      className="w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-700 hover:bg-blue-50 hover:text-blue-700 flex items-center justify-between transition-colors group cursor-pointer"
                    >
                      <span>{skName}</span>
                      <ArrowRight className="w-3 h-3 text-slate-400 group-hover:text-blue-600 transition-colors" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Matching Students */}
            {matchingStudents.length > 0 && (
              <div className="p-2.5">
                <span className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 px-2 py-1 flex items-center gap-1.5">
                  <Users className="w-3 h-3 text-indigo-600" /> Matching Students
                </span>
                <div className="space-y-1 mt-1">
                  {matchingStudents.map((st) => (
                    <button
                      key={st.id}
                      type="button"
                      onClick={() => handleSelectStudentSuggestion(st)}
                      className="w-full text-left p-2 rounded-xl text-xs hover:bg-slate-50 flex items-center gap-2.5 transition-colors group cursor-pointer"
                    >
                      <ProfileAvatar
                        src={st.avatar || st.avatar_url}
                        name={st.name}
                        email={st.email}
                        size="xs"
                        className="rounded-full shrink-0"
                      />
                      <div className="flex-1 min-w-0">
                        <p className="font-bold text-slate-900 truncate group-hover:text-blue-600 transition-colors">
                          {st.name}
                        </p>
                        <p className="text-[11px] text-slate-400 truncate">
                          {st.role || st.branch || 'Student'}
                        </p>
                      </div>
                      <span className="text-[10px] font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full shrink-0">
                        View
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* View all results footer */}
            <div className="p-2 bg-slate-50/80 text-center">
              <button
                type="button"
                onClick={() => handleSearchSubmit()}
                className="text-xs font-bold text-blue-600 hover:text-blue-700 transition-colors py-1 cursor-pointer"
              >
                Press <kbd className="px-1 py-0.5 bg-white border border-slate-200 rounded text-[10px] font-mono">Enter</kbd> to see all results in Explore
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Right Header Controls */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Mobile Search Button */}
        <button
          onClick={() => navigate('/app/explore')}
          className="sm:hidden p-2 text-slate-600 hover:text-slate-900 rounded-xl hover:bg-slate-100 transition-colors cursor-pointer"
          title="Search"
        >
          <Search className="w-5 h-5" />
        </button>

        {/* Notifications Icon */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2.5 text-slate-600 hover:text-slate-900 rounded-xl hover:bg-slate-100 transition-colors cursor-pointer"
            title="Notifications"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-2 right-2 w-2.5 h-2.5 bg-blue-600 rounded-full ring-2 ring-white" />
            )}
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-2xl border border-slate-200 shadow-xl z-50 p-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
                <h3 className="font-semibold text-slate-900 text-sm">Notifications</h3>
                {unreadCount > 0 && (
                  <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full">
                    {unreadCount} new
                  </span>
                )}
              </div>

              <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
                {notifications.length > 0 ? (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      className="p-3 rounded-xl border text-xs bg-white border-slate-100 flex gap-3"
                    >
                      <div className="flex-1">
                        <p className="font-semibold text-slate-900">{n.title}</p>
                        <p className="text-slate-600 line-clamp-2 mt-0.5">{n.message}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="py-6 text-center text-xs text-slate-400">
                    No notifications yet.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Avatar */}
        <div
          onClick={() => navigate('/app/profile')}
          className="flex items-center gap-2 pl-2 cursor-pointer group"
        >
          <ProfileAvatar
            src={profile?.avatar_url}
            name={displayName}
            email={user?.email}
            genderPreference={profile?.gender_preference}
            size="sm"
            className="rounded-full border-2 border-white shadow-xs group-hover:ring-2 group-hover:ring-blue-500/50 transition-all"
          />
          <span className="hidden md:block text-sm font-semibold text-slate-800 group-hover:text-blue-600 transition-colors max-w-[120px] truncate">
            {displayName}
          </span>
        </div>

        {/* Mobile Logout Button (Prominently accessible on mobile/tablet screens) */}
        <button
          onClick={() => {
            logout();
            navigate('/login');
          }}
          className="lg:hidden p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors cursor-pointer"
          title="Log out"
          aria-label="Log out"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
}
