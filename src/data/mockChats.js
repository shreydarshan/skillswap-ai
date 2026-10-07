// DEMO DATA
// Used only for UI development/testing.
// Not used as authenticated user data.

export const MOCK_CHATS = [
  {
    id: 'chat-1',
    participantId: 'user-1',
    participantName: 'Sophia Chen',
    participantAvatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&auto=format&fit=crop&q=80',
    participantRole: 'UI/UX Design Major',
    status: 'online',
    lastMessage: 'Sounds great! I prepared the Figma file for our session tomorrow.',
    lastMessageTime: '10:42 AM',
    unreadCount: 2,
    swapContext: {
      offering: 'Figma UI/UX Design',
      receiving: 'React.js',
      status: 'Active Swap'
    },
    messages: [
      {
        id: 'm1',
        senderId: 'user-1',
        text: 'Hey Alex! Saw your profile match for React and Figma. Would love to swap skills!',
        time: 'Yesterday 3:15 PM'
      },
      {
        id: 'm2',
        senderId: 'user-0',
        text: 'Hi Sophia! Absolutely, I have been wanting to level up my Figma auto-layout and components.',
        time: 'Yesterday 3:20 PM'
      },
      {
        id: 'm3',
        senderId: 'user-1',
        text: 'Awesome! We can meet at Green Library or Zoom. How is Thursday 3 PM for you?',
        time: 'Yesterday 3:45 PM'
      },
      {
        id: 'm4',
        senderId: 'user-0',
        text: 'Thursday 3 PM works perfectly. I will prepare a sample React app we can build together.',
        time: 'Yesterday 4:02 PM'
      },
      {
        id: 'm5',
        senderId: 'user-1',
        text: 'Sounds great! I prepared the Figma file for our session tomorrow.',
        time: '10:42 AM'
      }
    ]
  },
  {
    id: 'chat-2',
    participantId: 'user-2',
    participantName: 'Marcus Vance',
    participantAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80',
    participantRole: 'AI & Data Science Scholar',
    status: 'offline',
    lastMessage: 'Can you check out this PyTorch notebook when you get a chance?',
    lastMessageTime: 'Yesterday',
    unreadCount: 0,
    swapContext: {
      offering: 'Machine Learning',
      receiving: 'JavaScript',
      status: 'Pending Agreement'
    },
    messages: [
      {
        id: 'm6',
        senderId: 'user-2',
        text: 'Hey Alex, interested in doing a 1-on-1 swap on PyTorch neural network fundamentals?',
        time: 'Yesterday 1:10 PM'
      },
      {
        id: 'm7',
        senderId: 'user-2',
        text: 'Can you check out this PyTorch notebook when you get a chance?',
        time: 'Yesterday 1:12 PM'
      }
    ]
  },
  {
    id: 'chat-3',
    participantId: 'user-3',
    participantName: 'Elena Rostova',
    participantAvatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&auto=format&fit=crop&q=80',
    participantRole: 'Linguistics & Spanish Lit',
    status: 'online',
    lastMessage: '¡Hola! Ready for Spanish conversation practice next Tuesday?',
    lastMessageTime: 'Oct 4',
    unreadCount: 0,
    swapContext: {
      offering: 'Spanish Conversation',
      receiving: 'Python Basics',
      status: 'Completed (1 Session)'
    },
    messages: [
      {
        id: 'm8',
        senderId: 'user-3',
        text: '¡Hola Alex! Thanks for the Python installation help yesterday!',
        time: 'Oct 4 2:00 PM'
      },
      {
        id: 'm9',
        senderId: 'user-3',
        text: '¡Hola! Ready for Spanish conversation practice next Tuesday?',
        time: 'Oct 4 2:05 PM'
      }
    ]
  }
];
