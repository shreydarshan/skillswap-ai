import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useSearchParams } from 'react-router-dom';
import {
  Send,
  Search,
  MessageSquare,
  ArrowLeftRight,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  RefreshCw,
  Sparkles,
  Award,
  BookOpen
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/auth';
import Button from '../components/common/Button';
import ProfileAvatar from '../components/profile/ProfileAvatar';
import SkillTag from '../components/common/SkillTag';

export default function ChatsPage() {
  const { user, refreshSwaps } = useAuth();
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();

  // Tab: 'messages' or 'swaps'
  const initialTab = searchParams.get('tab') === 'swaps' ? 'swaps' : 'messages';
  const [activeTab, setActiveTab] = useState(initialTab);

  // Messages state
  const [messages, setMessages] = useState([]);
  const [allStudents, setAllStudents] = useState([]);
  const [activePartnerId, setActivePartnerId] = useState(null);
  const [selectedPartner, setSelectedPartner] = useState(null);
  const [messageInput, setMessageInput] = useState('');
  const [sending, setSending] = useState(false);
  const [sendError, setSendError] = useState(null);
  const [searchFilter, setSearchFilter] = useState('');

  // Swap requests state
  const [swapRequests, setSwapRequests] = useState([]);
  const [actionInProgress, setActionInProgress] = useState({});
  const [swapActionError, setSwapActionError] = useState(null);
  const [swapToComplete, setSwapToComplete] = useState(null);
  const [completing, setCompleting] = useState(false);

  // Global loading
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const messagesEndRef = useRef(null);

  // Scroll to bottom of active conversation
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Load all messages, swaps, and student directory
  const loadData = async (isSilent = false) => {
    if (!isSilent) setLoading(true);
    else setRefreshing(true);

    try {
      const [msgs, swaps, students] = await Promise.all([
        authService.getMyMessages().catch(() => []),
        authService.getMySwapRequests().catch(() => []),
        authService.getStudents().catch(() => [])
      ]);

      setMessages(Array.isArray(msgs) ? msgs : []);
      setSwapRequests(Array.isArray(swaps) ? swaps : []);
      setAllStudents(Array.isArray(students) ? students : []);
    } catch (err) {
      console.warn('Error loading chat/swap data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [user]);

  // Handle incoming navigation state (e.g., from "Send Message" in Profile Modal)
  useEffect(() => {
    const passedRecipientId = location.state?.recipientId || searchParams.get('userId');
    const passedUser = location.state?.recipientUser;

    if (passedRecipientId) {
      setActivePartnerId(passedRecipientId);
      setActiveTab('messages');
      if (passedUser) {
        setSelectedPartner(passedUser);
      }
    }
  }, [location.state, searchParams]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, activePartnerId]);

  // Extract unique conversation partners from messages
  const conversationPartnersMap = new Map();

  messages.forEach((m) => {
    const partnerId = m.sender_id === user?.id ? m.receiver_id : m.sender_id;
    const partnerName = m.sender_id === user?.id ? m.receiver_name : m.sender_name;
    const partnerAvatar = m.sender_id === user?.id ? m.receiver_avatar : m.sender_avatar;

    if (!conversationPartnersMap.has(partnerId)) {
      // Cross-reference with allStudents directory if available
      const studentDir = allStudents.find((s) => s.id === partnerId);
      conversationPartnersMap.set(partnerId, {
        id: partnerId,
        name: studentDir?.name || partnerName || 'Student',
        email: studentDir?.email || '',
        avatar: studentDir?.avatar || studentDir?.avatar_url || partnerAvatar,
        role: studentDir?.role || studentDir?.branch || 'Student',
        university: studentDir?.university || studentDir?.college || '',
        lastMessage: m.message,
        lastTime: m.created_at,
      });
    } else {
      const existing = conversationPartnersMap.get(partnerId);
      existing.lastMessage = m.message;
      existing.lastTime = m.created_at;
    }
  });

  // If a partner was selected via profile modal navigation that has no prior messages
  if (activePartnerId && !conversationPartnersMap.has(activePartnerId)) {
    const studentDir = allStudents.find((s) => s.id === activePartnerId) || selectedPartner;
    conversationPartnersMap.set(activePartnerId, {
      id: activePartnerId,
      name: studentDir?.name || studentDir?.full_name || 'Student',
      email: studentDir?.email || '',
      avatar: studentDir?.avatar || studentDir?.avatar_url,
      role: studentDir?.role || studentDir?.branch || 'Student',
      university: studentDir?.university || studentDir?.college || '',
      lastMessage: 'New conversation started',
      lastTime: new Date().toISOString(),
    });
  }

  const conversationPartners = Array.from(conversationPartnersMap.values());

  // Filter partners by search
  const filteredPartners = conversationPartners.filter((p) =>
    (p.name || '').toLowerCase().includes(searchFilter.toLowerCase().trim())
  );

  // Active partner resolution
  const effectivePartnerId = activePartnerId || (conversationPartners[0] ? conversationPartners[0].id : null);
  const activePartner =
    conversationPartners.find((p) => p.id === effectivePartnerId) ||
    allStudents.find((s) => s.id === effectivePartnerId) ||
    selectedPartner;

  // Active messages thread
  const activeMessages = messages.filter(
    (m) =>
      (m.sender_id === user?.id && m.receiver_id === effectivePartnerId) ||
      (m.sender_id === effectivePartnerId && m.receiver_id === user?.id)
  );

  // Active swap with partner if any
  const activeSwapWithPartner = swapRequests.find(
    (s) =>
      s.status === 'ACCEPTED' &&
      ((s.sender_id === user?.id && s.receiver_id === effectivePartnerId) ||
        (s.receiver_id === user?.id && s.sender_id === effectivePartnerId))
  );

  // Send a new message
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!effectivePartnerId) return;
    const cleanContent = messageInput.trim();
    if (!cleanContent) return;

    setSending(true);
    setSendError(null);

    try {
      const createdMessage = await authService.sendMessage(effectivePartnerId, cleanContent);
      setMessages((prev) => [...prev, createdMessage]);
      setMessageInput('');
    } catch (err) {
      setSendError(err.message || 'Failed to send message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  // Swap Requests Breakdown
  const incomingRequests = swapRequests.filter((s) => s.receiver_id === user?.id);
  const sentRequests = swapRequests.filter((s) => s.sender_id === user?.id);
  const pendingIncomingCount = incomingRequests.filter((s) => s.status === 'PENDING').length;

  const handleAcceptSwap = async (swapId) => {
    setActionInProgress((prev) => ({ ...prev, [swapId]: true }));
    setSwapActionError(null);
    try {
      const updated = await authService.acceptSwapRequest(swapId);
      setSwapRequests((prev) => prev.map((s) => (s.id === swapId ? updated : s)));
      if (refreshSwaps) refreshSwaps();
    } catch (err) {
      setSwapActionError(err.message || 'Failed to accept swap request.');
    } finally {
      setActionInProgress((prev) => ({ ...prev, [swapId]: false }));
    }
  };

  const handleDeclineSwap = async (swapId) => {
    setActionInProgress((prev) => ({ ...prev, [swapId]: true }));
    setSwapActionError(null);
    try {
      const updated = await authService.declineSwapRequest(swapId);
      setSwapRequests((prev) => prev.map((s) => (s.id === swapId ? updated : s)));
      if (refreshSwaps) refreshSwaps();
    } catch (err) {
      setSwapActionError(err.message || 'Failed to decline swap request.');
    } finally {
      setActionInProgress((prev) => ({ ...prev, [swapId]: false }));
    }
  };

  const handleCompleteSwap = async (swapId) => {
    setCompleting(true);
    setSwapActionError(null);
    try {
      const updated = await authService.completeSwapRequest(swapId);
      setSwapRequests((prev) => prev.map((s) => (s.id === swapId ? updated : s)));
      setSwapToComplete(null);
      if (refreshSwaps) refreshSwaps();
    } catch (err) {
      setSwapActionError(err.message || 'Failed to complete swap request.');
    } finally {
      setCompleting(false);
    }
  };

  if (loading) {
    return (
      <div className="h-[calc(100vh-8.5rem)] bg-white rounded-3xl border border-slate-200 shadow-sm flex items-center justify-center text-slate-400 text-sm">
        <div className="flex items-center gap-2">
          <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
          <span>Loading conversations & swap requests...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-8rem)] min-h-[560px] bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden flex flex-col animate-in fade-in duration-200">
      {/* Top Header & Tab Switcher */}
      <div className="px-5 py-3.5 border-b border-slate-200 bg-white flex items-center justify-between gap-4 shrink-0">
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              setActiveTab('messages');
              setSearchParams({});
            }}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
              activeTab === 'messages'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Direct Messages</span>
          </button>

          <button
            onClick={() => {
              setActiveTab('swaps');
              setSearchParams({ tab: 'swaps' });
            }}
            className={`relative px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
              activeTab === 'swaps'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <ArrowLeftRight className="w-3.5 h-3.5" />
            <span>Swap Requests</span>
            {pendingIncomingCount > 0 && (
              <span className="px-1.5 py-0.2 bg-amber-500 text-white text-[10px] font-extrabold rounded-full animate-pulse">
                {pendingIncomingCount}
              </span>
            )}
          </button>
        </div>

        <button
          onClick={() => loadData(true)}
          disabled={refreshing}
          className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-colors cursor-pointer"
          title="Refresh messages and swaps"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-blue-600' : ''}`} />
        </button>
      </div>

      {/* TAB CONTENT 1: DIRECT MESSAGES */}
      {activeTab === 'messages' && (
        <div className="flex-1 flex flex-col md:flex-row overflow-hidden min-h-0">
          {/* Left Column: Conversation Sidebar */}
          <div className="w-full md:w-80 lg:w-96 border-r border-slate-200 flex flex-col shrink-0 bg-slate-50/50">
            {/* Search filter */}
            <div className="p-3 border-b border-slate-200 bg-white">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
                <input
                  type="text"
                  value={searchFilter}
                  onChange={(e) => setSearchFilter(e.target.value)}
                  placeholder="Search students..."
                  className="w-full pl-8 pr-3 py-1.5 bg-slate-100 border border-slate-200 rounded-xl text-xs focus:outline-none focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Conversation list */}
            <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
              {filteredPartners.length === 0 ? (
                <div className="p-6 text-center text-xs text-slate-400">
                  <MessageSquare className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                  <p className="font-semibold text-slate-600">No active conversations</p>
                  <p className="mt-1">
                    Visit student profiles in Recommendations or Explore to message peers.
                  </p>
                </div>
              ) : (
                filteredPartners.map((partner) => {
                  const isSelected = partner.id === effectivePartnerId;
                  return (
                    <div
                      key={partner.id}
                      onClick={() => {
                        setActivePartnerId(partner.id);
                        setSelectedPartner(partner);
                      }}
                      className={`p-3.5 flex items-center gap-3 cursor-pointer transition-colors ${
                        isSelected
                          ? 'bg-blue-50/80 border-l-4 border-blue-600'
                          : 'hover:bg-slate-100/70'
                      }`}
                    >
                      <ProfileAvatar
                        src={partner.avatar}
                        name={partner.name}
                        email={partner.email}
                        size="md"
                        className="rounded-2xl shrink-0"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <h4 className="text-xs font-bold text-slate-900 truncate">
                            {partner.name}
                          </h4>
                          {partner.lastTime && (
                            <span className="text-[10px] text-slate-400 shrink-0">
                              {new Date(partner.lastTime).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-500 truncate mt-0.5">
                          {partner.lastMessage || partner.role || 'Connected'}
                        </p>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Right Column: Chat Conversation Stream */}
          <div className="flex-1 flex flex-col bg-white overflow-hidden min-h-0">
            {activePartner ? (
              <>
                {/* Active Chat Header */}
                <div className="px-5 py-3 border-b border-slate-200 flex items-center justify-between bg-white shrink-0">
                  <div className="flex items-center gap-3">
                    <ProfileAvatar
                      src={activePartner.avatar}
                      name={activePartner.name}
                      email={activePartner.email}
                      size="sm"
                      className="rounded-xl shrink-0"
                    />
                    <div>
                      <h3 className="font-bold text-slate-900 text-sm">{activePartner.name}</h3>
                      <p className="text-[11px] text-slate-500">
                        {activePartner.role || 'Student'}{' '}
                        {activePartner.university ? `• ${activePartner.university}` : ''}
                      </p>
                    </div>
                  </div>

                  {activeSwapWithPartner && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSwapToComplete(activeSwapWithPartner)}
                      className="text-xs text-emerald-700 hover:text-emerald-800 hover:bg-emerald-50 border-emerald-200 font-medium"
                    >
                      Complete Swap
                    </Button>
                  )}
                </div>

                {/* Messages Stream */}
                <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-3 bg-slate-50/30">
                  {activeMessages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center p-6 text-xs text-slate-400">
                      <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-3">
                        <Sparkles className="w-6 h-6" />
                      </div>
                      <p className="font-bold text-slate-700 text-sm">
                        Start your conversation with {activePartner.name}
                      </p>
                      <p className="mt-1 max-w-xs text-slate-500">
                        Coordinate skill sessions, set up study dates, or ask questions!
                      </p>
                    </div>
                  ) : (
                    activeMessages.map((msg) => {
                      const isMe = msg.sender_id === user?.id;
                      return (
                        <div
                          key={msg.id}
                          className={`flex ${isMe ? 'justify-end' : 'justify-start'} animate-in fade-in duration-150`}
                        >
                          <div
                            className={`max-w-[78%] sm:max-w-[70%] rounded-2xl px-4 py-2.5 text-xs ${
                              isMe
                                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-br-xs shadow-xs'
                                : 'bg-white border border-slate-200 text-slate-800 rounded-bl-xs shadow-2xs'
                            }`}
                          >
                            <p className="leading-relaxed whitespace-pre-wrap break-words">{msg.message}</p>
                            <div
                              className={`text-[9px] mt-1 text-right font-medium ${
                                isMe ? 'text-blue-100' : 'text-slate-400'
                              }`}
                            >
                              {new Date(msg.created_at).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </div>
                          </div>
                        </div>
                      );
                    })
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Send Message Input */}
                <div className="p-3.5 border-t border-slate-200 bg-white shrink-0">
                  {sendError && (
                    <div className="mb-2 p-2 bg-rose-50 text-rose-700 border border-rose-200 rounded-xl text-xs flex items-center gap-1.5">
                      <AlertCircle className="w-3.5 h-3.5 text-rose-500 shrink-0" />
                      <span>{sendError}</span>
                    </div>
                  )}
                  <form onSubmit={handleSendMessage} className="flex items-center gap-2">
                    <input
                      type="text"
                      value={messageInput}
                      onChange={(e) => setMessageInput(e.target.value)}
                      placeholder={`Message ${activePartner.name}...`}
                      disabled={sending}
                      className="flex-1 px-4 py-2.5 bg-slate-100 border border-slate-200 rounded-xl text-xs focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                    />
                    <Button
                      type="submit"
                      variant="primary"
                      size="md"
                      disabled={sending || !messageInput.trim()}
                      icon={Send}
                    >
                      {sending ? 'Sending...' : 'Send'}
                    </Button>
                  </form>
                </div>
              </>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-slate-400 text-xs">
                <MessageSquare className="w-12 h-12 text-slate-300 mb-3" />
                <p className="font-semibold text-slate-700 text-sm">Select a Conversation</p>
                <p className="mt-1 max-w-xs text-slate-500">
                  Pick a conversation from the left to read messages or start chatting.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB CONTENT 2: SWAP REQUESTS LIFECYCLE */}
      {activeTab === 'swaps' && (
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-6">
          {swapActionError && (
            <div className="p-3 bg-rose-50 text-rose-700 border border-rose-200 rounded-2xl text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-500 shrink-0" />
              <span>{swapActionError}</span>
            </div>
          )}

          {/* 1. INCOMING SWAP REQUESTS (RECEIVER VIEW) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <span>Incoming Swap Requests</span>
                {pendingIncomingCount > 0 && (
                  <span className="px-2 py-0.5 bg-amber-100 text-amber-800 text-[10px] font-bold rounded-full">
                    {pendingIncomingCount} Pending Action
                  </span>
                )}
              </h3>
            </div>

            {incomingRequests.length === 0 ? (
              <div className="p-8 text-center bg-slate-50 rounded-2xl border border-slate-200/60 text-xs text-slate-400">
                <Clock className="w-6 h-6 text-slate-300 mx-auto mb-1.5" />
                <span>No incoming swap requests at this time.</span>
              </div>
            ) : (
              <div className="grid gap-3 sm:grid-cols-2">
                {incomingRequests.map((swap) => {
                  const isPending = swap.status === 'PENDING';
                  const isAccepted = swap.status === 'ACCEPTED';
                  const isRejected = swap.status === 'REJECTED';
                  const inAction = actionInProgress[swap.id];

                  return (
                    <div
                      key={swap.id}
                      className="p-4 rounded-2xl border bg-white border-slate-200 shadow-2xs space-y-3 hover:border-slate-300 transition-colors"
                    >
                      {/* From Header */}
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2.5">
                          <ProfileAvatar
                            src={swap.sender_avatar}
                            name={swap.sender_name || 'Student'}
                            size="sm"
                            className="rounded-xl shrink-0"
                          />
                          <div>
                            <span className="text-[10px] uppercase font-bold text-slate-400 block leading-none">
                              From
                            </span>
                            <span className="text-xs font-bold text-slate-900">
                              {swap.sender_name || 'Student'}
                            </span>
                          </div>
                        </div>

                        {/* Status Badge */}
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            isPending
                              ? 'bg-amber-50 text-amber-700 border border-amber-200'
                              : isAccepted
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : isRejected
                              ? 'bg-rose-50 text-rose-700 border border-rose-200'
                              : 'bg-blue-50 text-blue-700 border border-blue-200'
                          }`}
                        >
                          {isPending ? 'Pending' : isAccepted ? 'Accepted' : isRejected ? 'Declined' : swap.status}
                        </span>
                      </div>

                      {/* Offered and Requested Skills */}
                      <div className="space-y-1.5 bg-slate-50 p-2.5 rounded-xl border border-slate-100 text-xs">
                        <div className="flex items-center gap-1.5 text-blue-800">
                          <Award className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                          <span className="font-semibold text-[11px]">They Offer:</span>
                          <span className="font-bold text-slate-800">{swap.skill_offered_name}</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-emerald-800">
                          <BookOpen className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                          <span className="font-semibold text-[11px]">They Want:</span>
                          <span className="font-bold text-slate-800">{swap.skill_requested_name}</span>
                        </div>
                      </div>

                      {/* Proposal Message */}
                      {swap.message && (
                        <p className="text-xs text-slate-600 italic bg-slate-50/50 p-2 rounded-lg border border-slate-100">
                          "{swap.message}"
                        </p>
                      )}

                      {/* Action Buttons for Pending or Accepted */}
                      {isPending && (
                        <div className="pt-1 flex items-center justify-end gap-2 border-t border-slate-100">
                          <Button
                            variant="outline"
                            size="sm"
                            disabled={inAction}
                            onClick={() => handleDeclineSwap(swap.id)}
                            className="text-rose-600 hover:text-rose-700 hover:bg-rose-50 border-rose-200"
                          >
                            Decline
                          </Button>
                          <Button
                            variant="primary"
                            size="sm"
                            disabled={inAction}
                            onClick={() => handleAcceptSwap(swap.id)}
                          >
                            Accept
                          </Button>
                        </div>
                      )}
                      {isAccepted && (
                        <div className="pt-1 flex items-center justify-end gap-2 border-t border-slate-100">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setSwapToComplete(swap)}
                            className="text-xs text-slate-600 hover:text-emerald-700 hover:border-emerald-300"
                          >
                            Complete Swap
                          </Button>
                          <Button
                            variant="primary"
                            size="sm"
                            icon={MessageSquare}
                            onClick={() => {
                              setActiveTab('messages');
                              setActivePartnerId(swap.sender_id);
                            }}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white"
                          >
                            Open Chat
                          </Button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* 2. MY SENT REQUESTS (SENDER VIEW) */}
          <div className="space-y-3 pt-4 border-t border-slate-200">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
              My Sent Requests
            </h3>

            {sentRequests.length === 0 ? (
              <div className="p-8 text-center bg-slate-50 rounded-2xl border border-slate-200/60 text-xs text-slate-400">
                <Clock className="w-6 h-6 text-slate-300 mx-auto mb-1.5" />
                <span>You have not sent any swap proposals yet.</span>
              </div>
            ) : (
              <div className="grid gap-3 sm:grid-cols-2">
                {sentRequests.map((swap) => {
                  const isPending = swap.status === 'PENDING';
                  const isAccepted = swap.status === 'ACCEPTED';
                  const isRejected = swap.status === 'REJECTED';

                  return (
                    <div
                      key={swap.id}
                      className="p-4 rounded-2xl border bg-white border-slate-200 shadow-2xs space-y-3"
                    >
                      {/* To Header */}
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2.5">
                          <ProfileAvatar
                            src={swap.receiver_avatar}
                            name={swap.receiver_name || 'Student'}
                            size="sm"
                            className="rounded-xl shrink-0"
                          />
                          <div>
                            <span className="text-[10px] uppercase font-bold text-slate-400 block leading-none">
                              To
                            </span>
                            <span className="text-xs font-bold text-slate-900">
                              {swap.receiver_name || 'Student'}
                            </span>
                          </div>
                        </div>

                        {/* Status Badge */}
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            isPending
                              ? 'bg-amber-50 text-amber-700 border border-amber-200'
                              : isAccepted
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : isRejected
                              ? 'bg-rose-50 text-rose-700 border border-rose-200'
                              : 'bg-blue-50 text-blue-700 border border-blue-200'
                          }`}
                        >
                          {isPending ? 'Pending' : isAccepted ? 'Accepted' : isRejected ? 'Declined' : swap.status}
                        </span>
                      </div>

                      {/* Offered and Requested Skills */}
                      <div className="space-y-1.5 bg-slate-50 p-2.5 rounded-xl border border-slate-100 text-xs">
                        <div className="flex items-center gap-1.5 text-blue-800">
                          <Award className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                          <span className="font-semibold text-[11px]">You Offer:</span>
                          <span className="font-bold text-slate-800">{swap.skill_offered_name}</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-emerald-800">
                          <BookOpen className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                          <span className="font-semibold text-[11px]">You Want:</span>
                          <span className="font-bold text-slate-800">{swap.skill_requested_name}</span>
                        </div>
                      </div>

                      {/* Status summary message */}
                      <div className="text-[11px] text-slate-500 pt-1 flex items-center justify-between">
                        <span>
                          {isPending
                            ? 'Awaiting student response...'
                            : isAccepted
                            ? '🎉 Request accepted! Start chatting.'
                            : isRejected
                            ? 'Request declined.'
                            : 'Swap completed.'}
                        </span>
                        {isAccepted && (
                          <div className="flex items-center gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setSwapToComplete(swap)}
                              className="text-xs text-slate-600 hover:text-emerald-700 hover:border-emerald-300"
                            >
                              Complete Swap
                            </Button>
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => {
                                setActiveTab('messages');
                                setActivePartnerId(swap.receiver_id);
                              }}
                            >
                              Open Chat
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Complete Swap Confirmation Modal */}
      {swapToComplete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-md rounded-2xl border border-slate-200 p-6 shadow-2xl space-y-4">
            <div className="flex items-start gap-3">
              <div className="p-2.5 bg-emerald-50 text-emerald-600 rounded-xl shrink-0">
                <CheckCircle2 className="w-6 h-6 stroke-[2.5]" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">Complete this skill swap?</h3>
                <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                  Your active connection will end, but previous messages and swap history will remain available.
                </p>
              </div>
            </div>
            <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-slate-100">
              <Button
                variant="outline"
                size="sm"
                disabled={completing}
                onClick={() => setSwapToComplete(null)}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                disabled={completing}
                onClick={() => handleCompleteSwap(swapToComplete.id)}
                className="bg-emerald-600 hover:bg-emerald-700 text-white"
              >
                {completing ? 'Completing...' : 'Confirm & Complete'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
