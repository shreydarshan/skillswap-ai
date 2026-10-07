import { fetchApi } from './api';

export const authService = {
  // Authentication
  async register(email, password, fullName) {
    const data = await fetchApi('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName })
    });
    if (data.access_token) {
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    return data;
  },

  async login(email, password) {
    const data = await fetchApi('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    if (data.access_token) {
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    return data;
  },

  async getMe() {
    return await fetchApi('/auth/me');
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    try {
      return userStr ? JSON.parse(userStr) : null;
    } catch (e) {
      return null;
    }
  },

  getToken() {
    return localStorage.getItem('token');
  },

  // Real Profile Management
  async getMyProfile() {
    return await fetchApi('/profile/me');
  },

  async updateMyProfile(profileData) {
    return await fetchApi('/profile/me', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    });
  },

  // Real User Skills Management
  async getMySkills() {
    return await fetchApi('/profile/me/skills');
  },

  async addMySkill(skillName, skillType, proficiency = 4, category = 'General') {
    return await fetchApi('/profile/me/skills', {
      method: 'POST',
      body: JSON.stringify({
        skill_name: skillName,
        skill_type: skillType,
        proficiency,
        category
      })
    });
  },

  async removeMySkill(userSkillId) {
    return await fetchApi(`/profile/me/skills/${userSkillId}`, {
      method: 'DELETE'
    });
  },

  // Account Deletion
  async deleteAccount() {
    const res = await fetchApi('/auth/account', {
      method: 'DELETE'
    });
    this.logout();
    return res;
  },

  // Database-driven Candidate Students
  async getStudents() {
    return await fetchApi('/students');
  },

  // Database-driven Skill Categories
  async getSkillCategories() {
    return await fetchApi('/skills/categories');
  },

  // Messages & Unread Count
  async getMyMessages() {
    return await fetchApi('/messages/me');
  },

  async sendMessage(receiverId, message) {
    return await fetchApi('/messages', {
      method: 'POST',
      body: JSON.stringify({
        receiver_id: receiverId,
        message
      })
    });
  },

  async getConversationMessages(otherUserId) {
    return await fetchApi(`/messages/conversations/${otherUserId}`);
  },

  async getUnreadMessagesCount() {
    return await fetchApi('/messages/me/unread-count');
  },

  // Real Reciprocal Recommendation Engine API (Stage 5B)
  async getRecommendations(limit = 50) {
    return await fetchApi(`/recommendations?limit=${limit}`);
  },

  async getRecommendationMatch(candidateUserId) {
    return await fetchApi(`/recommendations/match/${candidateUserId}`);
  },

  // Collaborative Filtering Recommendation API (Stage 5D)
  async getCollaborativeRecommendations(limit = 50) {
    return await fetchApi(`/recommendations/collaborative?limit=${limit}`);
  },

  // Final Hybrid Recommendation Engine API (Stage 5E)
  async getHybridRecommendations(limit = 50) {
    return await fetchApi(`/recommendations/hybrid?limit=${limit}`);
  },

  // Genuine Interaction Tracking API (Stage 5C)
  async recordInteraction(targetUserId, interactionType) {
    return await fetchApi('/interactions', {
      method: 'POST',
      body: JSON.stringify({
        target_user_id: targetUserId,
        interaction_type: interactionType
      })
    });
  },

  async getMyInteractions() {
    return await fetchApi('/interactions/me');
  },

  // Real Skill Swap Request Lifecycle (Stage 5C)
  async sendSwapRequest({ receiverId, skillOfferedName, skillRequestedName, message }) {
    return await fetchApi('/swap-requests', {
      method: 'POST',
      body: JSON.stringify({
        receiver_id: receiverId,
        skill_offered_name: skillOfferedName,
        skill_requested_name: skillRequestedName,
        message
      })
    });
  },

  async acceptSwapRequest(swapId) {
    return await fetchApi(`/swap-requests/${swapId}/accept`, {
      method: 'PUT'
    });
  },

  async declineSwapRequest(swapId) {
    return await fetchApi(`/swap-requests/${swapId}/decline`, {
      method: 'PUT'
    });
  },

  async completeSwapRequest(swapId) {
    return await fetchApi(`/swap-requests/${swapId}/complete`, {
      method: 'PUT'
    });
  },

  async getMySwapRequests() {
    return await fetchApi('/swap-requests/me');
  },

  async getRelationshipWithUser(otherUserId) {
    return await fetchApi(`/swap-requests/relationship/${otherUserId}`);
  }
};
