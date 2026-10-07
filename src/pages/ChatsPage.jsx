import React, { useState, useEffect } from 'react';
import {
  Send,
  Paperclip,
  Smile,
  MoreVertical,
  Phone,
  Video,
  Sparkles,
  Calendar,
  CheckCheck,
  Search,
  BookOpen,
  MessageSquare
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/auth';
import Button from '../components/common/Button';
import EmptyState from '../components/common/EmptyState';

export default function ChatsPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadMessages() {
      setLoading(true);
      try {
        const msgs = await authService.getMyMessages();
        setMessages(Array.isArray(msgs) ? msgs : []);
      } catch (err) {
        console.warn('Failed to load user messages:', err);
        setMessages([]);
      } finally {
        setLoading(false);
      }
    }
    loadMessages();
  }, []);

  if (loading) {
    return (
      <div className="h-[calc(100vh-8rem)] bg-white rounded-2xl border border-slate-200 shadow-sm flex items-center justify-center text-slate-400 text-sm">
        Loading conversations...
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="h-[calc(100vh-8rem)] bg-white rounded-2xl border border-slate-200 shadow-sm flex items-center justify-center p-8">
        <EmptyState
          title="No conversations yet."
          description="Your conversations will appear here after you connect with a skill partner."
          icon={MessageSquare}
        />
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-8rem)] bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col md:flex-row animate-in fade-in duration-300">
      {/* Left Column: Conversations Sidebar */}
      <div className="w-full md:w-80 lg:w-96 border-r border-slate-200 flex flex-col shrink-0 bg-slate-50/50">
        <div className="p-4 border-b border-slate-200 bg-white">
          <h2 className="font-bold text-slate-900 text-lg mb-3">Messages & Swaps</h2>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search conversations..."
              className="w-full pl-9 pr-4 py-2 bg-slate-100 border border-slate-200 text-slate-900 rounded-xl text-xs focus:outline-none focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto divide-y divide-slate-100 p-4 text-xs text-slate-500 text-center">
          Showing {messages.length} message(s)
        </div>
      </div>

      {/* Right Column */}
      <div className="flex-1 flex flex-col bg-white h-full min-w-0 p-4">
        {messages.map((m) => (
          <div key={m.id} className="p-2 border-b text-xs text-slate-700">
            {m.content || m.text}
          </div>
        ))}
      </div>
    </div>
  );
}
