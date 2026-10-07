// DEMO DATA
// Used only for UI development/testing.
// Not used as authenticated user data.

export const MOCK_NOTIFICATIONS = [
  {
    id: 'n1',
    type: 'request',
    title: 'New Skill Swap Request',
    message: 'Sophia Chen requested a swap: Figma UI/UX Design for React.js',
    time: '15 minutes ago',
    unread: true,
    user: {
      name: 'Sophia Chen',
      avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80'
    }
  },
  {
    id: 'n2',
    type: 'match',
    title: 'High Compatibility Match! 🌟',
    message: '98% match detected with Marcus Vance for Machine Learning tutoring.',
    time: '2 hours ago',
    unread: true,
    user: {
      name: 'Marcus Vance',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80'
    }
  },
  {
    id: 'n3',
    type: 'review',
    title: 'New 5-Star Review Received',
    message: 'Marcus Vance left a review for your Python peer session.',
    time: '1 day ago',
    unread: false,
    user: {
      name: 'Marcus Vance',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80'
    }
  },
  {
    id: 'n4',
    type: 'system',
    title: 'Profile Endorsement',
    message: 'Elena Rostova endorsed your "React.js" skill!',
    time: '3 days ago',
    unread: false,
    user: null
  }
];
