import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Settings, Shield, Bell, User, Lock, CheckCircle2, Globe, Sliders, Trash2, AlertTriangle, X, LogOut } from 'lucide-react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/auth';

export default function SettingsPage() {
  const navigate = useNavigate();
  const { user, profile, logout } = useAuth();
  const [emailNotifs, setEmailNotifs] = useState(true);
  const [matchAlerts, setMatchAlerts] = useState(true);
  const [publicProfile, setPublicProfile] = useState(true);
  const [campusOnly, setCampusOnly] = useState(false);
  const [saved, setSaved] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState(null);

  const fullName = user?.full_name || profile?.full_name || '';
  const email = user?.email || '';
  const collegeName = profile?.college || profile?.university || 'your campus';

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleDeleteAccount = async () => {
    setDeleteError(null);
    setDeleting(true);
    try {
      await authService.deleteAccount();
      logout();
      navigate('/login');
    } catch (err) {
      setDeleteError(err.message || 'Failed to delete account. Please try again.');
      setDeleting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
          Account & Preference Settings
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Manage your SkillSwap AI preferences, notifications, and campus verification options.
        </p>
      </div>

      {saved && (
        <div className="p-4 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-2xl flex items-center gap-3 text-xs font-semibold animate-in slide-in-from-top-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <span>Your settings have been saved successfully!</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Campus & Account Info */}
        <Card className="space-y-4">
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <User className="w-4 h-4 text-blue-600" /> Student Verification & Account
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-medium text-slate-600 mb-1">Full Name</label>
              <input
                type="text"
                readOnly
                value={fullName}
                className="w-full px-3 py-2 bg-slate-100 border border-slate-200 rounded-xl text-slate-800 cursor-not-allowed"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-600 mb-1">Account Email</label>
              <input
                type="email"
                readOnly
                value={email}
                className="w-full px-3 py-2 bg-slate-100 border border-slate-200 rounded-xl text-slate-800 cursor-not-allowed"
              />
            </div>
          </div>

          <div className="p-3 bg-amber-50/80 rounded-xl border border-amber-200 flex items-center justify-between text-xs text-amber-900">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-amber-600" />
              <span>Campus Verification Status: <strong>Campus verification: Pending</strong></span>
            </div>
            <span className="px-2.5 py-0.5 bg-amber-500 text-white font-semibold rounded-full text-[10px]">
              Pending
            </span>
          </div>
        </Card>

        {/* AI Matching Preferences */}
        <Card className="space-y-4">
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <Sliders className="w-4 h-4 text-indigo-600" /> Recommendation Preferences
          </h3>

          <div className="space-y-3 text-xs">
            <label className="flex items-center justify-between p-3 bg-slate-50 rounded-xl cursor-pointer">
              <div>
                <span className="font-bold text-slate-800 block">Instant Match Alerts</span>
                <span className="text-slate-500">Notify me whenever a new compatibility match is found</span>
              </div>
              <input
                type="checkbox"
                checked={matchAlerts}
                onChange={(e) => setMatchAlerts(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </label>

            <label className="flex items-center justify-between p-3 bg-slate-50 rounded-xl cursor-pointer">
              <div>
                <span className="font-bold text-slate-800 block">Restrict Matches to My Campus</span>
                <span className="text-slate-500">Only match me with students from {collegeName}</span>
              </div>
              <input
                type="checkbox"
                checked={campusOnly}
                onChange={(e) => setCampusOnly(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </label>
          </div>
        </Card>

        {/* Notifications & Privacy */}
        <Card className="space-y-4">
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <Bell className="w-4 h-4 text-amber-600" /> Notifications & Privacy
          </h3>

          <div className="space-y-3 text-xs">
            <label className="flex items-center justify-between p-3 bg-slate-50 rounded-xl cursor-pointer">
              <div>
                <span className="font-bold text-slate-800 block">Email Digest Notifications</span>
                <span className="text-slate-500">Receive weekly summaries of swap requests and reviews</span>
              </div>
              <input
                type="checkbox"
                checked={emailNotifs}
                onChange={(e) => setEmailNotifs(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </label>

            <label className="flex items-center justify-between p-3 bg-slate-50 rounded-xl cursor-pointer">
              <div>
                <span className="font-bold text-slate-800 block">Public Profile Visibility</span>
                <span className="text-slate-500">Allow other students on campus to view my skills and bio</span>
              </div>
              <input
                type="checkbox"
                checked={publicProfile}
                onChange={(e) => setPublicProfile(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </label>
          </div>
        </Card>

        {/* Form Actions */}
        <div className="flex justify-end gap-3">
          <Button type="submit" variant="primary" size="lg">
            Save Preferences
          </Button>
        </div>
      </form>

      {/* Account Session Management */}
      <Card className="space-y-4">
        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
          <LogOut className="w-4 h-4 text-slate-600" /> Account Session
        </h3>
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-xs">
          <div>
            <span className="font-bold text-slate-900 block">Sign Out</span>
            <span className="text-slate-500">End your active authenticated session on this browser device.</span>
          </div>
          <Button
            type="button"
            variant="outline"
            size="md"
            onClick={() => {
              logout();
              navigate('/login');
            }}
            icon={LogOut}
          >
            Log Out
          </Button>
        </div>
      </Card>

      {/* DANGER ZONE: Account Deletion */}
      <Card className="border-rose-200 bg-rose-50/40 space-y-4">
        <h3 className="text-sm font-bold text-rose-800 uppercase tracking-wider flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-600" /> Danger Zone
        </h3>

        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-xs">
          <div>
            <span className="font-bold text-slate-900 block">Delete Account</span>
            <span className="text-slate-500">This permanently deletes your account and associated data.</span>
          </div>
          <Button
            type="button"
            variant="danger"
            size="md"
            onClick={() => setShowDeleteModal(true)}
            icon={Trash2}
          >
            Delete Account
          </Button>
        </div>
      </Card>

      {/* Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-md rounded-2xl border border-slate-200 shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2 text-rose-600 font-bold text-base">
                <AlertTriangle className="w-5 h-5" />
                <span>Delete your SkillSwap account?</span>
              </div>
              <button
                onClick={() => setShowDeleteModal(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {deleteError && (
              <div className="p-3 bg-rose-50 text-rose-800 rounded-xl text-xs font-semibold">
                {deleteError}
              </div>
            )}

            <p className="text-xs text-slate-600 leading-relaxed">
              This will permanently remove your:
            </p>
            <ul className="text-xs text-slate-600 list-disc list-inside space-y-1 font-medium pl-1">
              <li>account</li>
              <li>profile</li>
              <li>skills</li>
              <li>swap requests</li>
              <li>messages</li>
              <li>ratings</li>
              <li>interactions</li>
            </ul>

            <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-3">
              <Button
                variant="outline"
                size="md"
                onClick={() => setShowDeleteModal(false)}
                disabled={deleting}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                size="md"
                onClick={handleDeleteAccount}
                disabled={deleting}
                icon={Trash2}
              >
                {deleting ? 'Deleting Account...' : 'Delete My Account'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
