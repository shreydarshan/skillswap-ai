import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, Compass, Users, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/auth';
import SearchBar from '../components/common/SearchBar';
import ExploreStudentCard from '../components/profile/ExploreStudentCard';
import EmptyState from '../components/common/EmptyState';

const CATEGORY_LIST = [
  { id: 'all', label: 'All' },
  { id: 'coding', label: 'Programming & Web', keywords: ['programming', 'web', 'frontend', 'backend', 'coding', 'react', 'python', 'java', 'html', 'css', 'kotlin', 'software'] },
  { id: 'design', label: 'UI/UX & Design', keywords: ['design', 'ui/ux', 'graphic', 'figma', 'illustration'] },
  { id: 'data', label: 'Data & AI', keywords: ['data', 'ai', 'machine learning', 'analytics', 'data science', 'python'] },
  { id: 'languages', label: 'Languages', keywords: ['foreign languages', 'language', 'spanish', 'french', 'german', 'english', 'mandarin', 'japanese'] },
  { id: 'math', label: 'Math & Physics', keywords: ['math', 'physics', 'calculus', 'algebra', 'science'] },
  { id: 'media', label: 'Media', keywords: ['media', 'video', 'audio', 'production', 'editing', 'film'] },
  { id: 'business', label: 'Business', keywords: ['business', 'marketing', 'finance', 'public speaking', 'seo'] },
];

export default function ExplorePage() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [students, setStudents] = useState([]);

  const initialQuery = searchParams.get('q') || '';
  const [searchVal, setSearchVal] = useState(initialQuery);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(true);
  const [swapToast, setSwapToast] = useState(null);

  // Sync search input with URL search parameter if changed externally (e.g. from global search)
  useEffect(() => {
    const q = searchParams.get('q') || '';
    setSearchVal(q);
  }, [searchParams]);

  useEffect(() => {
    async function loadExploreData() {
      setLoading(true);
      try {
        const studentsData = await authService.getStudents();
        setStudents(Array.isArray(studentsData) ? studentsData : []);
      } catch (err) {
        console.warn('Failed to load explore data from backend:', err);
      } finally {
        setLoading(false);
      }
    }
    loadExploreData();
  }, []);

  // Update search state & URL query parameter cleanly
  const handleSearchChange = (val) => {
    setSearchVal(val);
    if (val.trim()) {
      setSearchParams({ q: val.trim() }, { replace: true });
    } else {
      setSearchParams({}, { replace: true });
    }
  };

  // 1. Deduplicate by unique user ID & filter out authenticated user and test accounts
  const seenIds = new Set();
  const candidatePool = [];
  for (const s of students) {
    const sid = s.id || s.user_id;
    if (!sid) continue;
    if (sid === user?.id || s.email === user?.email) continue;
    if (s.is_test || (s.email && s.email.includes('test_'))) continue;
    if (seenIds.has(sid)) continue;
    seenIds.add(sid);
    candidatePool.push(s);
  }

  // 2. Filter by search query across name, college, branch, and offered/wanted skills
  const filteredStudents = candidatePool.filter((student) => {
    const query = searchVal.toLowerCase().trim();
    const studentName = (student.name || student.full_name || '').toLowerCase();
    const studentRole = (student.role || student.branch || '').toLowerCase();
    const studentUniv = (student.university || student.college || '').toLowerCase();

    const offeredNames = (student.skillsOffered || student.skills_offered || []).map((sk) =>
      typeof sk === 'string' ? sk.toLowerCase() : (sk.name || '').toLowerCase()
    );
    const wantedNames = (student.skillsWanted || student.skills_wanted || []).map((sk) =>
      typeof sk === 'string' ? sk.toLowerCase() : (sk.name || '').toLowerCase()
    );

    const matchesQuery =
      !query ||
      studentName.includes(query) ||
      studentRole.includes(query) ||
      studentUniv.includes(query) ||
      offeredNames.some((sk) => sk.includes(query)) ||
      wantedNames.some((sk) => sk.includes(query));

    if (!matchesQuery) return false;

    // Category Filter: Check if any offered or wanted skill belongs to the selected category
    if (selectedCategory !== 'all') {
      const catDef = CATEGORY_LIST.find((c) => c.id === selectedCategory);
      if (catDef && catDef.keywords) {
        const allSkills = [...(student.skillsOffered || []), ...(student.skillsWanted || [])];
        const hasMatchingSkill = allSkills.some((s) => {
          const sName = (typeof s === 'string' ? s : s.name || '').toLowerCase();
          const sCat = (typeof s === 'object' ? s.category || '' : '').toLowerCase();
          return catDef.keywords.some((kw) => sName.includes(kw) || sCat.includes(kw));
        });
        if (!hasMatchingSkill) return false;
      }
    }

    return true;
  });

  const handleSwapSuccess = (targetUser, offer, want) => {
    setSwapToast(`Request submitted to ${targetUser.name || targetUser.full_name}! (${offer} ↔ ${want})`);
    setTimeout(() => setSwapToast(null), 4000);
  };

  return (
    <div className="space-y-6 sm:space-y-7 animate-in fade-in duration-300">
      {/* Toast Notification */}
      {swapToast && (
        <div className="fixed top-20 right-6 z-50 bg-slate-900 text-white px-4 py-3 rounded-2xl shadow-2xl border border-slate-800 flex items-center gap-3">
          <span className="w-2 h-2 rounded-full bg-emerald-400" />
          <span className="text-xs font-semibold">{swapToast}</span>
        </div>
      )}

      {/* EXPLORE HEADER — Campus Directory Identity */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-100 inline-block mb-1.5">
            Campus Directory
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Explore
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1 font-medium">
            Discover students, skills and swap opportunities across campus.
          </p>
        </div>

        {!loading && (
          <div className="px-3.5 py-1.5 bg-white border border-slate-200/90 rounded-2xl shadow-2xs self-start sm:self-auto text-xs font-semibold text-slate-600">
            Showing <span className="text-blue-600 font-bold">{filteredStudents.length}</span> students
          </div>
        )}
      </div>

      {/* SEARCH BAR */}
      <div>
        <SearchBar
          value={searchVal}
          onChange={handleSearchChange}
          placeholder="Search students or skills..."
        />
      </div>

      {/* CLEAN CATEGORY FILTER PILLS (NO CONFUSING NUMBERS) */}
      <div className="space-y-2">
        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
          Category
        </span>
        <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
          {CATEGORY_LIST.map((cat) => {
            const isSelected = selectedCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all duration-150 shrink-0 cursor-pointer ${
                  isSelected
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'bg-slate-100 hover:bg-slate-200/80 text-slate-700'
                }`}
              >
                {cat.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* STUDENTS DIRECTORY GRID */}
      {loading ? (
        <div className="py-20 text-center text-slate-400 text-sm">
          Loading student candidates from database...
        </div>
      ) : filteredStudents.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredStudents.map((student) => (
            <ExploreStudentCard
              key={student.id}
              student={student}
              onSwapSuccess={handleSwapSuccess}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          title="No students matched your search"
          description="Try searching for another skill, student name, or clearing category filters."
          actionLabel={searchVal || selectedCategory !== 'all' ? 'Clear Filters' : undefined}
          onAction={() => {
            handleSearchChange('');
            setSelectedCategory('all');
          }}
        />
      )}
    </div>
  );
}
