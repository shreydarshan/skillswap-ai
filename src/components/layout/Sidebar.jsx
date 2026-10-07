import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Compass,
  PlusCircle,
  MessageSquare,
  User,
  Settings,
  Zap,
  BookOpen,
  LogOut
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { authService } from '../../services/auth';
import { getAvatarUrl } from '../../utils/avatar';
import ProfileAvatar from '../profile/ProfileAvatar';

export default function Sidebar() {
  const navigate = useNavigate();
  const { user, profile, logout } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    async function fetchUnread() {
      try {
        const data = await authService.getUnreadMessagesCount();
        setUnreadCount(data?.unread_count || 0);
      } catch (err) {
        setUnreadCount(0);
      }
    }
    fetchUnread();
  }, []);

  const navItems = [
    { label: 'Recommendations', path: '/app', icon: Sparkles, end: true },
    { label: 'Explore', path: '/app/explore', icon: Compass, end: false },
    { label: 'Post a Swap', path: '/app/post', icon: PlusCircle, end: false },
    { label: 'Messages', path: '/app/chats', icon: MessageSquare, badge: unreadCount > 0 ? unreadCount : null, end: false },
    { label: 'Profile', path: '/app/profile', icon: User, end: false },
    { label: 'Settings', path: '/app/settings', icon: Settings, end: false }
  ];

  const displayName = user?.full_name || profile?.full_name || user?.email || 'Student User';
  const collegeName = profile?.college || 'University Student';
  const avatarUrl = getAvatarUrl(profile?.avatar_url, displayName, user?.email);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="hidden lg:flex flex-col w-64 border-r border-slate-200 bg-white min-h-screen fixed left-0 top-0 bottom-0 z-30">
      {/* Brand Logo */}
      <div className="h-16 flex items-center px-6 border-b border-slate-100">
        <div 
          onClick={() => navigate('/app')}
          className="flex items-center gap-2.5 cursor-pointer group"
        >
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-blue-500 text-white flex items-center justify-center shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform duration-200">
            <Zap className="w-5 h-5 fill-white" />
          </div>
          <div>
            <span className="font-bold text-lg text-slate-900 tracking-tight leading-none block">
              SkillSwap <span className="text-blue-600">AI</span>
            </span>
            <span className="text-[10px] text-slate-400 font-medium tracking-wide uppercase block">
              Peer Learning Exchange
            </span>
          </div>
        </div>
      </div>

      {/* Primary Navigation */}
      <div className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        <div className="px-3 mb-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Main Menu
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 font-semibold shadow-2xs border border-blue-100/60'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="px-2 py-0.5 text-xs font-semibold bg-blue-600 text-white rounded-full">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </div>

      {/* Quick Post Banner */}
      <div className="p-4 mx-4 mb-4 rounded-2xl bg-gradient-to-br from-blue-50 via-indigo-50/50 to-white border border-blue-100/80">
        <div className="flex items-center gap-2 text-blue-700 font-semibold text-xs mb-1">
          <BookOpen className="w-3.5 h-3.5" />
          <span>Need a Tutor?</span>
        </div>
        <p className="text-xs text-slate-600 mb-3 leading-relaxed">
          Post what you want to learn & exchange skills with peers on campus.
        </p>
        <button
          onClick={() => navigate('/app/post')}
          className="w-full py-2 px-3 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow-xs transition-colors flex items-center justify-center gap-1.5"
        >
          <PlusCircle className="w-3.5 h-3.5" />
          Post New Request
        </button>
      </div>

      {/* User Footer Profile */}
      <div className="p-4 border-t border-slate-100 flex items-center justify-between">
        <div 
          onClick={() => navigate('/app/profile')}
          className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity overflow-hidden flex-1"
        >
          <ProfileAvatar
            src={profile?.avatar_url}
            name={displayName}
            email={user?.email}
            genderPreference={profile?.gender_preference}
            size="sm"
            className="rounded-full shrink-0"
          />
          <div className="overflow-hidden text-left flex-1 min-w-0">
            <h4 className="text-sm font-semibold text-slate-900 truncate leading-tight">
              {displayName}
            </h4>
            <p className="text-xs text-slate-500 truncate">
              {collegeName}
            </p>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-rose-50 transition-colors ml-1 shrink-0"
          title="Log out"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </aside>
  );
}
