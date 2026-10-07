import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(authService.getCurrentUser());
  const [profile, setProfile] = useState(null);
  const [userSkills, setUserSkills] = useState([]);
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

  // Restore authenticated session on page refresh
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
        } catch (err) {
          console.warn('Session expired or invalid token:', err);
          authService.logout();
          setUser(null);
          setProfile(null);
          setUserSkills([]);
        }
      }
      setLoading(false);
    }
    loadUser();
  }, []);

  const login = async (email, password) => {
    const data = await authService.login(email, password);
    setUser(data.user);
    try {
      const profileData = await authService.getMyProfile();
      setProfile(profileData);
      await fetchSkills();
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
        loading,
        isAuthenticated: !!user,
        login,
        signup,
        logout,
        refreshProfile,
        refreshSkills
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
