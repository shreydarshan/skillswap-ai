import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Compass, PlusCircle, ArrowLeftRight, MessageSquare } from 'lucide-react';

export default function QuickActions() {
  const navigate = useNavigate();

  const actions = [
    {
      label: 'Find a Skill',
      sublabel: 'Browse campus',
      icon: Compass,
      path: '/app/explore',
      color: 'text-blue-600',
      bg: 'bg-blue-50/80 hover:bg-blue-100/70',
      border: 'border-blue-100/80',
    },
    {
      label: 'Post a Swap',
      sublabel: 'Offer your skills',
      icon: PlusCircle,
      path: '/app/post',
      color: 'text-indigo-600',
      bg: 'bg-indigo-50/80 hover:bg-indigo-100/70',
      border: 'border-indigo-100/80',
    },
    {
      label: 'My Requests',
      sublabel: 'Track active swaps',
      icon: ArrowLeftRight,
      path: '/app/profile',
      color: 'text-emerald-600',
      bg: 'bg-emerald-50/80 hover:bg-emerald-100/70',
      border: 'border-emerald-100/80',
    },
    {
      label: 'Messages',
      sublabel: 'Chat with peers',
      icon: MessageSquare,
      path: '/app/chats',
      color: 'text-purple-600',
      bg: 'bg-purple-50/80 hover:bg-purple-100/70',
      border: 'border-purple-100/80',
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {actions.map((act) => {
        const Icon = act.icon;
        return (
          <button
            key={act.label}
            onClick={() => navigate(act.path)}
            className={`flex items-center gap-3 p-3.5 rounded-2xl border ${act.border} ${act.bg} transition-all duration-200 cursor-pointer text-left group hover:scale-[1.02] shadow-2xs`}
          >
            <div className={`p-2.5 rounded-xl bg-white shadow-2xs ${act.color} shrink-0 group-hover:scale-110 transition-transform`}>
              <Icon className="w-5 h-5" />
            </div>
            <div className="min-w-0">
              <span className="block text-xs sm:text-sm font-bold text-slate-900 truncate">
                {act.label}
              </span>
              <span className="block text-[11px] text-slate-500 font-medium truncate">
                {act.sublabel}
              </span>
            </div>
          </button>
        );
      })}
    </div>
  );
}
