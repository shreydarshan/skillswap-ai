import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(authService.getCurrentUser());
  const [profile, setProfile] = useState(null);
  const [userSkills, setUserSkills] = useState([]);
  const [mySwaps, setMySwaps] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchSkills = async () => {
    try {
      const skillsData = await authService.getMySkills();
      setUserSkills(Array.isArray(skillsData) ? skillsData : []);
    } catch (e) {
      console.warn('Could not fetch user skills', e);
      setUserSkills([]);
    }
  };

  const fetchSwaps = async () => {
    try {
      const swapsData = await authService.getMySwapRequests();
      setMySwaps(Array.isArray(swapsData) ? swapsData : []);
      return swapsData;
    } catch (e) {
      console.warn('Could not fetch user swap requests', e);
      setMySwaps([]);
    }
  };

  const getRelationshipWithUser = (targetUserId) => {
    if (!targetUserId || !user?.id) {
      return { status: 'NO_RELATIONSHIP', isConnected: false, isPending: false, direction: 'NONE', swap: null };
    }
    const tId = String(targetUserId).toLowerCase();
    const myId = String(user.id).toLowerCase();

    const relevant = (mySwaps || []).filter(s => {
      const sId = String(s.sender_id || '').toLowerCase();
      const rId = String(s.receiver_id || '').toLowerCase();
      return sId === tId || rId === tId;
    });

    const accepted = relevant.find(s => s.status === 'ACCEPTED');
    if (accepted) {
      return {
        status: 'CONNECTED',
        isConnected: true,
        isPending: false,
        direction: 'MUTUAL',
        swap: accepted
      };
    }

    const pending = relevant.find(s => s.status === 'PENDING');
    if (pending) {
      const isOutgoing = String(pending.sender_id).toLowerCase() === myId;
      return {
        status: 'PENDING',
        isConnected: false,
        isPending: true,
        direction: isOutgoing ? 'OUTGOING' : 'INCOMING',
        swap: pending
      };
    }

    const completed = relevant.find(s => s.status === 'COMPLETED');
    if (completed) {
      return {
        status: 'COMPLETED',
        isConnected: false,
        isPending: false,
        direction: 'MUTUAL',
        swap: completed
      };
    }

    return {
      status: 'NO_RELATIONSHIP',
      isConnected: false,
      isPending: false,
      direction: 'NONE',
      swap: null
    };
  };

  // Restore authenticated session on page refresh & maintain multi-tab sync
  useEffect(() => {
    async function loadUser() {
      const token = authService.getToken();
      if (token) {
        try {
          const userData = await authService.getMe();
          setUser(userData);
          localStorage.setItem('user', JSON.stringify(userData));

          const profileData = await authService.getMyProfile();
          setProfile(profileData);

          await fetchSkills();
          await fetchSwaps();
        } catch (err) {
          console.warn('Session check notice:', err);
          const currentToken = authService.getToken();
          const isAuthError = !currentToken || 
            (err.message && (
              err.message.toLowerCase().includes('credential') ||
              err.message.toLowerCase().includes('unauthorized') ||
              err.message.toLowerCase().includes('token') ||
              err.message.toLowerCase().includes('user no longer exists')
            ));

          if (isAuthError) {
            authService.logout();
            setUser(null);
            setProfile(null);
            setUserSkills([]);
            setMySwaps([]);
          } else {
            // Preserve session on temporary connection glitch/cold start
            const cachedUser = authService.getCurrentUser();
            if (cachedUser) {
              setUser(cachedUser);
            }
          }
        }
      } else {
        setUser(null);
        setProfile(null);
        setUserSkills([]);
        setMySwaps([]);
      }
      setLoading(false);
    }

    loadUser();

    // Listen for storage events to immediately synchronize state if account changes in another tab
    const handleStorageChange = (e) => {
      if (e.key === 'token' || e.key === 'user') {
        const currentToken = authService.getToken();
        const currentUser = authService.getCurrentUser();
        if (!currentToken) {
          setUser(null);
          setProfile(null);
          setUserSkills([]);
          setMySwaps([]);
        } else if (currentUser) {
          setUser(currentUser);
          authService.getMyProfile().then(setProfile).catch(() => {});
          fetchSkills();
          fetchSwaps();
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const login = async (email, password) => {
    const data = await authService.login(email, password);
    setUser(data.user);
    try {
      const profileData = await authService.getMyProfile();
      setProfile(profileData);
      await fetchSkills();
      await fetchSwaps();
    } catch (e) {
      console.warn('Could not fetch profile/skills after login', e);
    }
    return data;
  };

  const signup = async (email, password, fullName) => {
    const data = await authService.register(email, password, fullName);
    setUser(data.user);
    try {
      const profileData = await authService.getMyProfile();
      setProfile(profileData);
      await fetchSkills();
      await fetchSwaps();
    } catch (e) {
      console.warn('Could not fetch profile/skills after signup', e);
    }
    return data;
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setProfile(null);
    setUserSkills([]);
    setMySwaps([]);
  };

  const refreshProfile = async () => {
    try {
      const profileData = await authService.getMyProfile();
      setProfile(profileData);
      return profileData;
    } catch (e) {
      console.warn('Could not refresh profile', e);
    }
  };

  const refreshSkills = async () => {
    await fetchSkills();
  };

  const refreshSwaps = async () => {
    await fetchSwaps();
  };

  const offeredSkills = (userSkills || []).filter(s => s.skill_type === 'OFFER');
  const wantedSkills = (userSkills || []).filter(s => s.skill_type === 'WANT');

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        userSkills,
        offeredSkills,
        wantedSkills,
        mySwaps,
        loading,
        isAuthenticated: !!user,
        login,
        signup,
        logout,
        refreshProfile,
        refreshSkills,
        refreshSwaps,
        getRelationshipWithUser
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
