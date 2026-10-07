import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Sparkles,
  Compass,
  PlusCircle,
  MessageSquare,
  User
} from 'lucide-react';

export default function MobileNavigation() {
  const navItems = [
    { label: 'Match', path: '/app', icon: Sparkles, end: true },
    { label: 'Explore', path: '/app/explore', icon: Compass, end: false },
    { label: 'Post', path: '/app/post', icon: PlusCircle, end: false },
    { label: 'Chats', path: '/app/chats', icon: MessageSquare, badge: 2, end: false },
    { label: 'Profile', path: '/app/profile', icon: User, end: false }
  ];

  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md border-t border-slate-200 z-40 px-2 py-2">
      <div className="flex items-center justify-around max-w-md mx-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.end}
              className={({ isActive }) =>
                `relative flex flex-col items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'text-blue-600 font-semibold scale-105'
                    : 'text-slate-500 hover:text-slate-900'
                }`
              }
            >
              <div className="relative">
                <Icon className="w-5 h-5" />
                {item.badge && (
                  <span className="absolute -top-1 -right-2 px-1.5 py-0.2 text-[10px] font-bold bg-blue-600 text-white rounded-full">
                    {item.badge}
                  </span>
                )}
              </div>
              <span className="text-[11px] leading-none">{item.label}</span>
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
}
