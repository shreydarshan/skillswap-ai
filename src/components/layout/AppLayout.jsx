import React from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { AlertCircle, ArrowRight } from 'lucide-react';
import Sidebar from './Sidebar';
import Header from './Header';
import MobileNavigation from './MobileNavigation';
import { useAuth } from '../../context/AuthContext';
import { isProfileComplete } from '../../utils/profile';

export default function AppLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { profile, offeredSkills, wantedSkills, loading } = useAuth();

  const isSetupRoute = location.pathname.startsWith('/app/profile/setup');
  const complete = isProfileComplete(profile, offeredSkills, wantedSkills);

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Desktop Left Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 lg:pl-64 flex flex-col min-w-0 min-h-screen pb-20 lg:pb-8">
        {/* Header */}
        <Header />

        {/* Incomplete Profile Prompt Banner */}
        {!loading && !complete && !isSetupRoute && (
          <div className="bg-amber-500 text-white px-4 py-2.5 shadow-xs flex items-center justify-between text-xs font-semibold animate-in slide-in-from-top duration-200">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-white shrink-0" />
              <span>Complete your profile to start finding skill partners.</span>
            </div>
            <button
              onClick={() => navigate('/app/profile/setup')}
              className="bg-white text-amber-900 px-3 py-1 rounded-lg text-xs font-bold hover:bg-amber-50 transition-colors flex items-center gap-1"
            >
              Setup Profile <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        )}

        {/* Dynamic Route Pages */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full">
          <Outlet />
        </main>
      </div>

      {/* Mobile Bottom Navigation */}
      <MobileNavigation />
    </div>
  );
}
